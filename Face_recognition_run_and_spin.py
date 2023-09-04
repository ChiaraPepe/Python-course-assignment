#!/usr/bin/python3

# This script was implemented from https://picamera.readthedocs.io/en/release-1.13/recipes2.html and https://github.com/NoBlackBoxes/LastBlackBox/tree/master/course 
# Run this script, then point a web browser at http://<this-IP-address>:8000/index.html
# Note: needs simplejpeg to be installed (pip3 install simplejpeg).

import io
import logging
import socketserver
from http import server
from threading import Condition
import cv2
import numpy as np

import socket
import struct
import pyaudio

import serial
import time

from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput

PAGE = """\
<html>
<head>
<title>picamera2 MJPEG streaming demo</title>
</head>
<body>
<h1>Picamera2 MJPEG Streaming Demo</h1>
<img src="stream.mjpg" width="640" height="480" />
</body>
</html>
"""

# Configure serial port
ser = serial.Serial()
ser.baudrate = 19200
ser.port = '/dev/ttyUSB0'

# Open serial port
ser.open()
time.sleep(2.00) # Wait for connection before sending any data

#Setup the audio connection
CHUNK_SIZE = 4096           # Buffer size
FORMAT = pyaudio.paInt16    # Data type
CHANNELS = 2                # Number of channels
RATE = 22050                # Sample rate (Hz)

# Initialize PyAudio
audio = pyaudio.PyAudio()

# Open the audio stream
stream = audio.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK_SIZE)

class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()


class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame

                        ### The image is encoded in bytes,
                        ### needs to be converted to e.g. numpy array
                        frame = cv2.imdecode(np.frombuffer(frame, dtype=np.uint8),
                                             cv2.IMREAD_COLOR)
                        
                        
                        
                        #     ###############
                        #     ## HERE CAN GO ALL IMAGE PROCESSING
                        #     ###############
                        #frame = frame[::-1]
                        frame = frame[::-1].copy()
                        det = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

                        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                        rects = det.detectMultiScale(gray, 
                                                     scaleFactor=1.1, 
                                                     minNeighbors=5, 
                                                     minSize=(30, 30), # adjust to your image size, maybe smaller, maybe larger?
                                                     flags=cv2.CASCADE_SCALE_IMAGE)

                        for (x, y, w, h) in rects:
                            # x: x location
                            # y: y location
                            # w: width of the rectangle 
                            # h: height of the rectangle
                            # Remember, order in images: [y, x, channel]
                            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 20)
                            # Face detected. Send command to robot to run
                            ser.write(b'b')

                        cv2.imwrite("test_face.jpg", frame)
                            
                        #     ### and now we convert it back to JPEG to stream it
                    _, frame = cv2.imencode('.JPEG', frame)

                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
                    
                    # Read audio data from the stream
                    raw_data = stream.read(CHUNK_SIZE)

                    # Convert raw_data to left and right channel
                    interleaved_data = np.frombuffer(raw_data, dtype=np.int16)
                    left = interleaved_data[::2]
                    right = interleaved_data[1::2]

                    # Report volume (on left)
                    print("L: {0:.2f}, R: {1:.2f}".format(np.mean(np.abs(left)), np.mean(np.abs(right))))
                    value = float(np.mean(np.abs(left)))
                    
                    if value > 1000:
                        ser.write(b'b')
                        
                    
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()


class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True


picam2 = Picamera2()
picam2.configure(picam2.create_video_configuration(main={"size": (640, 480)}))
output = StreamingOutput()
picam2.start_recording(JpegEncoder(), FileOutput(output))

try:
    address = ('', 8000)
    server = StreamingServer(address, StreamingHandler)
    server.serve_forever()
finally:
    picam2.stop_recording()
    ser.close()
