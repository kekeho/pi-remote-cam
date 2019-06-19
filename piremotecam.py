# Copyright (c) 2019 Hiroki Takemura (kekeho)
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

from flask import Flask, render_template, Response, redirect
from flask_socketio import SocketIO, emit, send
import uuid
import zipfile
from datetime import datetime
from lib import video

app = Flask(__name__)
app.config['SECRET_KEY'] = str(uuid.uuid4)

socketio = SocketIO(app, async_mode='threading')
thread = None

camera = video.CamThread(save_dir='static/taken_images', socketio=socketio)
camera.start()

@app.route('/') 
def index(): 
    return render_template('index.html')


@app.route('/stream.mpeg') 
def video_feed(): 
    return Response(camera.get_frame(), 
                    mimetype='multipart/x-mixed-replace; boundary=frame') 


@app.route('/download')
def download():
    filename = datetime.now().strftime('%Y-%m-%d-%H-%M-%S') + '.zip'
    print(filename)
    with zipfile.ZipFile('static/zipfiles/' + filename, 'w', compression=zipfile.ZIP_DEFLATED) as zipfp:
        [ zipfp.write(p, arcname=p.split('/')[-1]) for p in camera.taken_photos ]
    
    return redirect('/static/zipfiles/' + filename)


@socketio.on('shot', namespace='/socket')
def shot(message):
    camera.shot()


@socketio.on('interval-shot', namespace='/socket')
def interval_shot(message):
    sec = int(message['sec'])
    camera.set_interval(sec)


@socketio.on('stop-interval', namespace='/socket')
def stop_interval(message):
    camera.clear_interval()


@socketio.on('get-all-taken-images', namespace='/socket')
def send_all_taken_images(message):
    emit('new-images', list(camera.taken_photos), namespace='/socket')


if __name__ == '__main__': 
    socketio.run(app, host='0.0.0.0')