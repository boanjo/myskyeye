"""
   Author: Igor Maculan - n3wtron@gmail.com
   A Simple mjpg stream http server
"""
import cv2
import threading
import http
import logging
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from SocketServer import ThreadingMixIn
import time
import sys
import os
import urllib
import requests
import numpy as np

class CamHandler(BaseHTTPRequestHandler):
    
    def __init__(self, request, client_address, server):
        img_src = 'http://{}:{}/cam.mjpg'.format(server.server_address[0], server.server_address[1])
        self.html_page = """
            <html>
                <head></head>
                <body>
                    <img src="{}"/>
                </body>
            </html>""".format(img_src)
        self.html_404_page = """
            <html>
                <head></head>
                <body>
                    <h1>NOT FOUND</h1>
                </body>
            </html>"""
        BaseHTTPRequestHandler.__init__(self, request, client_address, server)

    def do_GET(self):
        if self.path.endswith('live.mjpg'):
            self.send_response(200)
            self.send_header('Content-type', 'multipart/x-mixed-replace; boundary=--jpgboundary')
            self.end_headers()
            while True:
                try:
                    start = time.time()
                    if self.path.endswith('motion_live.mjpg'):                        
                        img = self.server.read_motion_frame()
                    else:
                        img = self.server.read_frame()
                    
                    retval, jpg = cv2.imencode('.jpg', img)
                    if not retval:
                        raise RuntimeError('Could not encode img to JPEG')
                    jpg_bytes = jpg.tobytes()
                    self.wfile.write("--jpgboundary\r\n".encode())
                    self.send_header('Content-type', 'image/jpeg')
                    self.send_header('Content-length', len(jpg_bytes))
                    self.end_headers()
                    self.wfile.write(jpg_bytes)
                    diff = time.time() - start
                    time.sleep(max(0, (self.server.read_delay - diff)))
                except (cv2.error):
                    logging.warning("Skipping frame")
                except (IOError, requests.ConnectionError):
                    break
        elif self.path.endswith('.mjpg'):

            list1 = self.path.split('/')
            # Get last part i.e. potential file name
            input_file = "output/" + list1[-1].replace(".mjpg", ".avi")
            if os.path.isfile(input_file):
                self.send_response(200)
                self.send_header('Content-type', 'multipart/x-mixed-replace; boundary=--jpgboundary')
                self.end_headers()
           
                video_capture = cv2.VideoCapture(input_file)

                # trick to get length of video
                video_capture.set(cv2.CAP_PROP_POS_AVI_RATIO,1)
                frame_count = video_capture.get(cv2.CAP_PROP_FRAME_COUNT)
                
                # trick to get length of video
                video_capture.set(cv2.CAP_PROP_POS_AVI_RATIO,0)

                frames = 0
                while True:
                    try:
                        start = time.time()
                        ret, frame = video_capture.read()
                        if ret == True:
                            frames = frames + 1
                            height, width, channels = frame.shape
                            pos = int((frames/frame_count) * width)
                            pos_x_start = max(pos-1, 0)
                            pos_x_stop = min(pos+1, width)
                            cv2.rectangle(frame,(0,height),(width,height-3),(0,255,0),3)
                            cv2.rectangle(frame,(pos_x_start,height),(pos_x_stop,height-25),(0,0,255),3)
                            retval, jpg = cv2.imencode('.jpg', frame)
                            if not retval:
                                raise RuntimeError('Could not encode img to JPEG')
                            
                            jpg_bytes = jpg.tobytes()
                            self.wfile.write("--jpgboundary\r\n".encode())
                            self.send_header('Content-type', 'image/jpeg')
                            self.send_header('Content-length', len(jpg_bytes))
                            self.end_headers()
                            self.wfile.write(jpg_bytes)
                            diff = time.time() - start
                            time.sleep(max(0, (self.server.read_delay - diff)))
                        else:
                            break
                    except (cv2.error):
                        logging.warning("Skipping frame")
                    except (IOError, requests.ConnectionError):
                        break
            else:
                self.send_response(300)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(self.html_404_page.encode())
                
        elif self.path.endswith('.html'):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(self.html_page.encode())
        else:
            self.send_response(300)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(self.html_404_page.encode())


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""
    def __init__(self, initial_frame, server_address, RequestHandlerClass, bind_and_activate=True):
        HTTPServer.__init__(self, server_address, RequestHandlerClass, bind_and_activate)
        self._frame = initial_frame
        self._motion_frame = initial_frame
        fps = 6
        self.read_delay = 1. / fps
        self._lock = threading.Lock()

    def set_frame(self, frame):
        with self._lock:
            self._frame = frame

    def read_frame(self):
        with self._lock:
            return self._frame

    def set_motion_frame(self, frame):
        with self._lock:
            self._motion_frame = frame

    def read_motion_frame(self):
        with self._lock:
            return self._motion_frame

    def serve_forever(self, poll_interval=0.5):
        try:
            HTTPServer.serve_forever(self, poll_interval)
        except KeyboardInterrupt:
            return


def main():
    logging.basicConfig(format='%(asctime)s %(message)s', stream=sys.stdout, level=logging.INFO)    
    blank_image = np.zeros((1280,720,3), np.uint8)
    server = ThreadedHTTPServer(blank_image, ('0.0.0.0', 9999), CamHandler)
    logging.info("MJPG Replay server started")
    server.serve_forever()


if __name__ == '__main__':
    main()

