############################################################################################################
############################################################################################################
##                                                                                                        ##
## Quart VueCutter (c)2024 Dieter Chvatal backend                                                         ##
##                                                                                                        ##
############################################################################################################
############################################################################################################

import asyncio
import json
import os
from pprint import pformat as pf
from pprint import pprint as pp
from quart import Quart, jsonify, render_template, request, redirect, url_for, send_file
from quart_cors import cors
import subprocess
import time


# overwrite jinja2 delimiters to avoid conflict with vue delimiters, was previosly used by me (Dieter Chvatal)
# in order to transfer information from the backend to the frontend, while the frontend does not know its host ip address.
# window.location.host and winndow.location.protocol is now used to get the host ip address. The code is left here for reference.
# https://stackoverflow.com/questions/37039835/how-to-change-jinja2-delimiters
class CustomQuart(Quart):
    jinja_options = Quart.jinja_options.copy()
    jinja_options.update(dict( block_start_string='<%', block_end_string='%>', variable_start_string='%%', 
                              variable_end_string='%%',comment_start_string='<#',comment_end_string='#>',))


# instantiate the app
# the frontend is built with vuetify.js and is located in the dist folder
# you have to set the static folder to the dist folder and the template folder to the dist folder in the backend like below
# and edit vite.config.js to output to the dist folder within the frontend. in adddition you have to
# run 'npm run build' after each modification of the frontend. Once you run this once, the included watch mode will
# take care of the rest.
app = CustomQuart(__name__, static_folder = "dist/static", template_folder = "dist", static_url_path = "/static")
app = cors(app, allow_origin="*")
app.config.from_object(__name__)


# uncomment to disable caching, which is useful for development when you are actively changing the frontend
@app.after_request
async def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for x minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response

# the functionality of the backend is provided by the Plexdata class, which is imported here
# the Plexdata class is a wrapper around the PlexAPI and the Cutter class
from dplexapi.dplexdata import Plexdata
plexdata = Plexdata(os.path.dirname(__file__))

# routes to provide xspf files for VLC -> would be a candidate to be moved in a separate Quart blueprint
# all movies in plex
@app.route('/streamall.xspf')
async def streamsectionall():
    b = await plexdata.streamsectionall()
    return await send_file(b, as_attachment=True,
         attachment_filename='streamall.xspf',
         mimetype='text/xspf+xml')
    
# all movies in the section
@app.route('/streamsection.xspf')
async def streamsection():
    b = await plexdata.streamsection()
    return await send_file(b, as_attachment=True,
         attachment_filename='streamsection.xspf',
         mimetype='text/xspf+xml')
    
# the selected movie
@app.route('/streamurl.xspf')
async def streamurl():
    b = await plexdata.streamurl()
    return await send_file(b, as_attachment=True,
         attachment_filename='streamurl.xspf',
         mimetype='text/xspf+xml')

# the backend provides the following routes to the frontend
# routes to select a section, a serie, a season, a movie, to update a section, a serie, a season, a movie
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

# route to get information about a movie
@app.route("/movie_info/", methods=['POST'])
async def set_movie_get_info():
    await request.get_data()
    if request.method == 'POST':
        req = json.loads(await request.body)
        return await plexdata._movie_info(req)

# route to get specific information for the cutting process
@app.route("/movie_cut_info")
async def get_movie_cut_info():
    return await plexdata._movie_cut_info()

# route to generate small pics for a timelind and deliver them to the frontend
@app.route("/timeline", methods=['POST'])
async def timeline():
    await request.get_data()
    if request.method == 'POST':
        req = json.loads(await request.body)
        r = await plexdata._timeline(req)
        return r 

# route to get a frame at a scpecific time position and deliver it to the frontend
@app.route("/frame/", methods=['POST'])
async def get_frame():
    await request.get_data()
    if request.method == 'POST':
        req = json.loads(await request.body)
        return { 'frame': url_for('static', filename= await plexdata._frame(req)) }

# route to get the actual post_time of the backend. This is used to update the frontend
@app.route("/pos")
async def get_pos():
    return { 'pos': plexdata._selection['pos_time'] }

# execute the cutting process. hand over the data to the rq worker
@app.route("/cut2", methods=['POST'])
async def do_cut2():
    await request.get_data()
    if request.method == 'POST':
        #req = await request.json
        req = json.loads(await request.body)
        return await plexdata._cut2(req)
        
# route to get the progress of the cutting process
@app.route("/progress")
async def progress():
    return await plexdata._doProgress()

# deliver the vuetify frontend
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
        asyncio.run(app.run_task(host='0.0.0.0', port=5200, debug=True))
    finally:
        try:
            plexdata.cutter.umount()
        except Exception:
            pass
        print('Bye!')