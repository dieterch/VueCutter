import asyncio
import json
import os
from pprint import pformat as pf
from pprint import pprint as pp
from quart import Quart, jsonify, render_template, request, redirect, url_for, send_file
from quart_cors import cors
import subprocess
import time

from dplexapi.dplexdata import Plexdata

plexdata = Plexdata()

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
        if req is not None:
            section_name = req['section']
            movie_name = req['movie']
            if movie_name != '':
                s = await plexdata._update_section(section_name)
                m = await plexdata._update_movie(movie_name)
                m_info = { 'movie_info': plexdata.plex.movie_rec(m) }
            else:
                if section_name == '':
                    s = await plexdata._update_section('Plex Recordings')
                m = await plexdata._update_movie('')
                m_info = { 'movie_info': plexdata.plex.movie_rec(m) }
            print(f"\nmovie_info: {req} -> \n{pf(m_info)}")
            return m_info
        else:
            print(await request.data)
            print(await request.json)
            print(req)
            return { 'movie_info': { 'duration': 0 } }

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
    t0 = time.time()
    if request.method == 'POST':
        req = json.loads(await request.body)
        print(req)
        basename = str(req['basename']); pos = int(req['pos']); l = int(req['l']); r = int(req['r']); 
        step = int(req['step']); size = req['size']
        m = plexdata._selection['movie']
        target = os.path.dirname(__file__) + "/dist/static/"+ basename
        tl = plexdata.cutter.gen_timeline(m.duration // 1000, pos, l, r, step)
        r = plexdata.cutter.timeline(m, target , size, tl)
        print(r)
        t1 = time.time()
        print(f"total:{(t1-t0):5.2f}")
    return r   

@app.route("/frame/", methods=['POST'])
async def get_frame():
    await request.get_data()
    if request.method == 'POST':
        req = json.loads(await request.body)
        if req is not None:
            m = await plexdata._update_movie(req['movie_name'])
            try:
                pic_name = await plexdata.cutter.aframe(m ,req['pos_time'] ,os.path.dirname(__file__) + "/dist/static/")
                ret = { 'frame': url_for('static', filename=pic_name) }
                print(f"frame: {req} -> {ret}")
                return ret
            except subprocess.CalledProcessError as e:
                print(f"\nframe throws error:\n{str(e)}\n") 
                ret = { 'frame': url_for('static', filename='error.jpg') }
                print(f"frame: {req} -> {ret}")
        else:
            print(await request.data)
            print(await request.body)
            return { 'frame': url_for('static', filename='error.jpg') }
        
@app.route("/pos")
async def get_pos():
    return { 'pos': plexdata._selection['pos_time'] }

@app.route("/")
async def index():
    return await render_template('index.html')

if __name__ == '__main__':
    print('''
\033[H\033[J
****************************************************
* Vue Quart WebCutter V0.01 (c)2024 Dieter Chvatal *
* Async Backend for Webcutter                      *
****************************************************
''')
    try:
        asyncio.run(app.run_task(host='0.0.0.0', debug=True))
    finally:
        try:
            plexdata.cutter.umount()
        except Exception:
            pass
  
