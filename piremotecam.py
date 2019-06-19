from flask import Flask, render_template, Response
from flask_socketio import SocketIO, emit
import uuid
from lib import video

app = Flask(__name__)
app.config['SECRET_KEY'] = str(uuid.uuid4)

socketio = SocketIO(app, async_mode='threading')
thread = None

@app.route('/') 
def index(): 
    return render_template('index.html')


@app.route('/stream.mpeg') 
def video_feed(): 
    return Response(video.video_frame_gen(), 
                    mimetype='multipart/x-mixed-replace; boundary=frame') 

if __name__ == '__main__': 
    socketio.run(app, host='0.0.0.0')