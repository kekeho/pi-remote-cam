# Copyright (c) 2019 Hiroki Takemura (kekeho)
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import io
import picamera
import threading
import os
import time
from datetime import datetime

# camera = picamera.PiCamera()

class CamThread(threading.Thread):
    def __init__(self, save_dir: str, socketio):
        super().__init__()
        self.frame = None
        self.camera = picamera.PiCamera()
        self.save_dir = save_dir
        self.shot_flag = False
        self.interval = None
        self.before_time = time.time()
        self.socketio = socketio
        self.taken_photos = set()  # filename set
        self.__chache_taken_photos = set()

    def run(self):
        while True:
            if self.shot_flag or (self.interval and (time.time() - self.before_time) > self.interval):
                self.__shot()
            else:
                with io.BytesIO() as stream:
                    self.camera.resolution = (320, 240)
                    self.camera.capture(stream, 'jpeg', use_video_port=True)
                    stream.seek(0)
                    frame = stream.read()
                self.frame = (b'--frame\r\n'
                            b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            self.__send_photo_list()

    def __shot(self):
        self.camera.resolution = (1640, 1232)
        filename = datetime.now().strftime('%Y-%m-%d-%H-%M-%S') + '.jpg'
        full_filename = os.path.join(self.save_dir, filename)
        self.camera.capture(full_filename)
        self.taken_photos.add(full_filename)

        self.shot_flag = False
        self.before_time = time.time()


    def shot(self):
        self.shot_flag = True
    

    def __send_photo_list(self):
        now = self.taken_photos.copy()
        new_photos = now - self.__chache_taken_photos
        if len(new_photos) > 0:
            self.socketio.emit('new-images', list(new_photos), namespace='/socket')
        self.__chache_taken_photos = now


    def set_interval(self, sec: int):
        self.interval = sec


    def clear_interval(self):
        self.shot_flag = False
        self.interval = None

    
    def get_frame(self):
        while True:
            yield self.frame
