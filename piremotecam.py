# Copyright (c) 2019 Hiroki Takemura (kekeho)
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

from flask import Flask, render_template, Response, redirect
from flask_socketio import SocketIO, emit, send
import uuid
import zipfile
from datetime import datetime
import os
from glob import glob
import subprocess
from lib import video


app = Flask(__name__)  # Flask app
app.config['SECRET_KEY'] = str(uuid.uuid4())  # Gen random secret key

socketio = SocketIO(app, async_mode='threading')  # socketio server
thread = None  # for contain thread list

# Generate camera instance
camera = video.CamThread(save_dir='static/taken_images', socketio=socketio)
camera.start()


@app.route('/')
def index():
    """Index page"""
    return render_template('index.html')


@app.route('/stream.mpeg')
def video_feed():
    """Stream realtime preview"""
    return Response(camera.get_frame(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/download')
def download():
    """Generate ZIP which contains taken images"""
    filename = datetime.now().strftime('%Y-%m-%d-%H-%M-%S') + \
        '.zip'  # '2019-06-20-23-21-49.zip'
    # Insert taken images to zipfile
    with zipfile.ZipFile('static/zipfiles/' + filename, 'w', compression=zipfile.ZIP_DEFLATED) as zipfp:
        [zipfp.write(p, arcname=p.split('/')[-1]) for p in camera.taken_photos]

    # Redirect to download link
    return redirect('/static/zipfiles/' + filename)


@socketio.on('shot', namespace='/socket')
def shot(message: dict):
    """Take a pic"""
    camera.shot()


@socketio.on('interval-shot', namespace='/socket')
def interval_shot(message: dict):
    """Set interval to camera"""
    sec = int(message['sec'])
    camera.set_interval(sec)


@socketio.on('stop-interval', namespace='/socket')
def stop_interval(message: dict):
    """Clear interval"""
    camera.clear_interval()


@socketio.on('get-all-taken-images', namespace='/socket')
def send_all_taken_images(message: dict):
    """Send already taken images in this session to client"""
    emit('new-images', list(camera.taken_photos), namespace='/socket')


@socketio.on('set-date', namespace='/socket')
def set_date(message: str):
    date = message
    print('Set time request:', date)
    cmd = ['sudo', 'date', '-s', date]
    result = subprocess.run(cmd).returncode

    emit('set-date-result', result, namespace='/socket')


@socketio.on('set-shutterspeed', namespace='/socket')
def set_shutterspeed(message: int):
    camera.set_shutterspoeed(message)


def remove_cache():
    del_imgs = glob('static/taken_images/*.jpg')
    [os.remove(x) for x in del_imgs]


if __name__ == '__main__':
    # remove_cache()  # TODO: create clear cache button
    socketio.run(app, host='0.0.0.0')
