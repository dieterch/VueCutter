import asyncio
import json
import os
from pprint import pformat as pf
from pprint import pprint as pp
from quart import Quart, jsonify, render_template, request, redirect, url_for, send_file
from quart_cors import cors
import subprocess
import time
import pytz
from redis import Redis
from rq import Connection, Queue, Worker
from rq.job import Job

from dplexapi.dplexdata import Plexdata

plexdata = Plexdata(os.path.dirname(__file__))

redis_connection = Redis(host='localhost',port=6379,password='63nTa6UlGeRipER5HIlInTH5hoS3ckL4', db=0)
q = Queue('VueCutter', connection=redis_connection, default_timeout=600)

# overwrite jinja2 delimiters to avoid conflict with vue delimiters
class CustomQuart(Quart):
    jinja_options = Quart.jinja_options.copy()
    jinja_options.update(dict(
        block_start_string='<%',
        block_end_string='%>',
        variable_start_string='%%',
        variable_end_string='%%',
        comment_start_string='<#',
        comment_end_string='#>',
    ))

# instantiate the app
app = CustomQuart(__name__,
            static_folder = "dist/static",
            template_folder = "dist",
            static_url_path = "/static"
            )
app = cors(app, allow_origin="*")
app.config.from_object(__name__)

# uncomment to disable caching
@app.after_request
async def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for x minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response

# sanity check route
@app.route('/ping', methods=['GET'])
async def ping_pong():
    return jsonify('pong!')

@app.route("/selection")
async def selection():
    return plexdata.get_selection()

@app.route("/update_section", methods=['POST'])
async def update_section():
    await request.get_data()
    if request.method == 'POST':
        req = json.loads(await request.body)
        await plexdata._update_section(req['section'])        
        print(f"update_section: {pf(req)}")
        return redirect(url_for('index'))

@app.route("/force_update_section")
async def force_update_section():
    await plexdata._update_section(plexdata._selection['section'].title, force=True)        
    print(f"force_update_section.")
    return redirect(url_for('index'))

@app.route("/update_serie", methods=['POST'])
async def update_serie():
    await request.get_data()
    if request.method == 'POST':
        req = json.loads(await request.body)
        await plexdata._update_serie(req['serie'])        
        print(f"update_serie: {pf(req)}")
        return redirect(url_for('index'))

@app.route("/update_season", methods=['POST'])
async def update_season():
    await request.get_data()
    if request.method == 'POST':
        req = json.loads(await request.body)
        await plexdata._update_season(req['season'])        
        print(f"update_season: {pf(req)}")
        return redirect(url_for('index'))

@app.route("/movie_info/", methods=['POST'])
async def set_movie_get_info():
    await request.get_data()
    if request.method == 'POST':
        req = json.loads(await request.body)
        return await plexdata._movie_info(req)

@app.route("/movie_cut_info")
async def get_movie_cut_info():
    return await plexdata._movie_cut_info()

@app.route('/streamall.xspf')
async def streamsectionall():
    b = await plexdata.streamsectionall()
    return await send_file(b, as_attachment=True,
         attachment_filename='streamall.xspf',
         mimetype='text/xspf+xml')

@app.route('/streamsection.xspf')
async def streamsection():
    b = await plexdata.streamsection()
    return await send_file(b, as_attachment=True,
         attachment_filename='streamsection.xspf',
         mimetype='text/xspf+xml')

@app.route('/streamurl.xspf')
async def streamurl():
    b = await plexdata.streamurl()
    return await send_file(b, as_attachment=True,
         attachment_filename='streamurl.xspf',
         mimetype='text/xspf+xml')

@app.route("/timeline", methods=['POST'])
async def timeline():
    await request.get_data()
    if request.method == 'POST':
        req = json.loads(await request.body)
        r = await plexdata._timeline(req)
        return r   

@app.route("/frame/", methods=['POST'])
async def get_frame():
    await request.get_data()
    if request.method == 'POST':
        req = json.loads(await request.body)
        return { 'frame': url_for('static', filename= await plexdata._frame(req)) }

@app.route("/pos")
async def get_pos():
    return { 'pos': plexdata._selection['pos_time'] }

@app.route("/cut2", methods=['POST'])
async def do_cut2():
    await request.get_data()
    if request.method == 'POST':
        #req = await request.json
        req = json.loads(await request.body)
        section_name = req['section']
        movie_name = req['movie_name']
        ss = req['ss']
        to = req['to']
        inplace = req['inplace']
        s = await plexdata._update_section(section_name)
        m = await plexdata._update_movie(movie_name)        
        res = f"Queue Cut From section '{s}', cut '{m.title}', In {ss}, Out {to}, inplace={inplace}"
        try:
            mm = plexdata.plex.MovieData(m)
            print("will cut now:\n",pf(res))
            job = q.enqueue_call(plexdata.cutter.cut, args=(mm,ss,to,inplace,))
            res = {
                'Section': s.title,
                'Duration Raw': mm.duration // 60000,
                'Duration Cut': plexdata.cutter.cutlength(ss,to),
                'In': ss,
                'Out': to,
                'Inplace': inplace,
                '.ap .sc Files': plexdata.cutter._apsc(m),
                'cut File': plexdata.cutter._cutfile(m)
            }
            return { 'result': res}
        except subprocess.CalledProcessError as e:
            print(str(e))
            return { 'result': str(e) }

async def doProgress():
    mstatus = {
        'title': '-',
        #'apsc_size': 0,
        'cut_progress': 0,
        'apsc_progress': 0,
        'started': 0,
        'status': 'idle'
    } 
    workers = Worker.all(connection=redis_connection)
    worker = workers[0] if len(workers) > 0 else None
    if worker:
        lhb = pytz.utc.localize(worker.last_heartbeat)
        lhbtz = lhb.astimezone(pytz.timezone("Europe/Vienna"))
        w = {
            'name': worker.name,
            'state': worker.state,
            'last_heartbeat': lhbtz.strftime("%H:%M:%S"),
            'current_job_id': worker.get_current_job_id(),
            'failed': worker.failed_job_count
        } 
    else:
        w = {
            'status':'no worker detected'
        }
    qd = {
        'started':q.started_job_registry.count,
        #'deferred':q.deferred_job_registry.count,
        'finished':q.finished_job_registry.count,
        #'scheduled':q.scheduled_job_registry.count,
        'failed':q.failed_job_registry.count,
    }
    if q.started_job_registry.count > 0:
        qd['started_jobs'] = []
        #qd['started_jobs'] = q.started_job_registry.get_job_ids()
        for job_id in q.started_job_registry.get_job_ids():
            job = Job.fetch(job_id, connection=redis_connection)
            m = plexdata.plex.MovieData(job.args[0])
            prog = plexdata.cutter._movie_stats(*job.args)
            apsc_prog = plexdata.cutter._apsc_stats(*job.args)
            #apsc_size = plexdata.cutter._apsc_size(m)
            #print(cutter._movie_stats(*job.args))
            d = {
                'title': m.title,
                'ss':job.args[1],
                'to':job.args[2],
                'name': job_id,
                'status':job.get_status(refresh=True),
                'cut_progress':prog,
                'apsc_progress':apsc_prog
            }
            qd['started_jobs'].append(d)
            mstatus.update({
                'title': m.title,
                #'apsc_size': apsc_size,
                'cut_progress': prog,
                'apsc_progress':apsc_prog,
                'started': q.started_job_registry.count,
                'status': d['status']           
            })

    if q.finished_job_registry.count > 0:
        qd['finished_jobs'] = []
        for job_id in q.finished_job_registry.get_job_ids():
            job = Job.fetch(job_id, connection=redis_connection)
            d = {
                'name': job_id,
                'result': job.result
            }
            qd['finished_jobs'].append(d) 

    return mstatus

@app.route("/progress")
async def progress():
    return await doProgress()

@app.route("/")
async def index():
    return await render_template('index.html')

if __name__ == '__main__':
    print('''
\033[H\033[J
****************************************************
* Vue Quart WebCutter V0.01 (c)2024 Dieter Chvatal *
* Async Backend                                    *
****************************************************
''')
    try:
        asyncio.run(app.run_task(host='0.0.0.0', port=5200, debug=False))
    finally:
        try:
            plexdata.cutter.umount()
        except Exception:
            pass
        print('Bye!')