# Copyright (c) 2019 Hiroki Takemura (kekeho)
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import io
import picamera
import threading
import os
import time
from flask_socketio import SocketIO
from datetime import datetime


class CamThread(threading.Thread):
    """Camera thread"""

    def __init__(self, save_dir: str, socketio: SocketIO):
        super().__init__()
        self.frame = b''  # Realtime image (Jpeg binary)
        self.camera = picamera.PiCamera()  # Camera object
        self.camera.shutter_speed = 0  # default: auto
        self.camera.framerate = 5
        self.save_dir = save_dir  # Place to save photos taken
        self.shot_flag = False  # if True: Shot in next loop
        self.interval = None  # Interval time (sec)
        self.before_time = time.time()  # Last time taken
        self.socketio = socketio  # socket object
        self.taken_photos = set()  # filename set
        self.recording_video_filename = None  # None: not recording, str: recording filename
        self.__chache_taken_photos = set()  # cache

    def run(self):
        # Loop
        while True:
            if self.shot_flag or (self.interval and (time.time() - self.before_time) > self.interval):
                # Shot
                self.__shot()
            else:
                # Realtime preview
                with io.BytesIO() as stream:  # in-memory file pointer
                    # self.camera.resolution = (320, 240)
                    self.camera.capture(stream, 'jpeg',
                                        use_video_port=False)  # Capture
                    stream.seek(0)
                    frame = stream.read()  # Get realtime frame
                self.frame = (b'--frame\r\n'
                              b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # add http header
            self.__send_photo_list()  # Send photo list to client

    def __shot(self):
        self.camera.resolution = (1640, 1232)  # High-resolution
        filename = datetime.now().strftime('%Y-%m-%d-%H-%M-%S') + '.jpg'
        full_filename = os.path.join(self.save_dir, filename)
        self.camera.capture(full_filename)  # Capture
        self.taken_photos.add('static/taken_images/' + filename)

        self.shot_flag = False
        self.before_time = time.time()  # Update last time taken

    def shot(self):
        self.shot_flag = True  # then, __shot called

    def __send_photo_list(self):
        """Send new photos list to client with socketio"""
        now = self.taken_photos.copy()
        new_photos = now - self.__chache_taken_photos
        if len(new_photos) > 0:
            # there is new photos
            self.socketio.emit('new-images', list(new_photos),
                               namespace='/socket')
        self.__chache_taken_photos = now  # update cache

    def set_interval(self, sec: int):
        """Set interval and start shooting"""
        self.interval = sec

    def clear_interval(self):
        """Clear interval, and stop shooting"""
        self.shot_flag = False
        self.interval = None

    def get_frame(self):
        """Get realtime frame"""
        while True:
            yield self.frame
    
    def set_shutterspoeed(self, micro_sec: int):
        """Set shutter speed
        Arg:
            micro_sec:
                > 0: exposure time [micro_seconds]
                0: auto
        """
        self.camera.shutter_speed = micro_sec
    
    def start_record_video(self):
        # self.camera.resolution = (1280, 720)  # High-resolution
        filename = datetime.now().strftime('%Y-%m-%d-%H-%M-%S') + '.h264'
        full_filename = os.path.join(self.save_dir, filename)

        self.recording_video_filename = 'static/taken_images/' + filename

        self.camera.start_recording(full_filename)  # Start recording
        print('Start recording')

    def stop_recording_video(self):
        if self.recording_video_filename == None:  # not recording
            return

        self.camera.stop_recording()  # Stop
        self.taken_photos.add(self.recording_video_filename)
        self.recording_video_filename = None
        print('Stop recording')
