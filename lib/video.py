# Copyright (c) 2019 Hiroki Takemura (kekeho)
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import io
import picamera
import threading

# camera = picamera.PiCamera()

class CamThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.frame = None
        self.camera = picamera.PiCamera()
    
    def run(self):
        while True:
            with io.BytesIO() as stream:
                self.camera.resolution = (320, 240)
                self.camera.capture(stream, 'jpeg', use_video_port=True)
                stream.seek(0)
                frame = stream.read()
            self.frame = (b'--frame\r\n'
                          b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    
    def get_frame(self):
        while True:
            yield self.frame
