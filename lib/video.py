# Copyright (c) 2019 Hiroki Takemura (kekeho)
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import io
import picamera

camera = picamera.PiCamera()

def video_frame_gen():
    """Get mpeg stream"""
    while True:
        with io.BytesIO() as stream:
            camera.resolution = (320, 240)
            camera.capture(stream, 'jpeg', use_video_port=True)
            stream.seek(0)
            frame = stream.read()

        yield (b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
