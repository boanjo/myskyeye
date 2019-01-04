import argparse
import os
import cv2
import sys
import psutil
import time
import logging
import utils.database as db
from utils.frame_worker import *
from utils.mjpg_streamer import ThreadedHTTPServer, CamHandler
import datetime
import threading
import multiprocessing
from multiprocessing import Queue, Pool
from Queue import PriorityQueue
from time import localtime, strftime

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

def process_frames(output_q, server):
    codec = cv2.VideoWriter_fourcc(*'XVID')  # cv2.cv.CV_FOURCC(*'XVID')

    font                   = cv2.FONT_HERSHEY_SIMPLEX
    fontScale              = 0.5
    fontColor              = (255,255,255)
    lineType               = 1

    best_frame = None
    best_weight = 0.0
    best_weight_display_count = 10
    STATE_SEARCHING = "searching"
    STATE_RECORDING = "recording"
    state = STATE_SEARCHING
    movement_count = 0
    time_str = ""
    timerTail = 0;
    acc_objects = set()
    prev_time = datetime.datetime.now()
    histogram = []
    x = 0
    while x < 31:
        histogram.append(0)
        x = x + 1

    while True:
        frame_number, data = output_q.get()

        movement = data['motion']
        frame_boxes = data['frame_boxes']
        #frame_thres = data['frame_thres']
        objects = data['important_objects']
        weight = data['weight']
        processing_time = data['processing_time']

        curr_time = datetime.datetime.now()
        diff = (curr_time - prev_time).microseconds
        prev_time = curr_time


        # produce 10ms index
        histogram_index = int(processing_time * 100)
        if histogram_index < 29:
            histogram[histogram_index] = histogram[histogram_index] + 1
        else:
            histogram[30] = histogram[30] + 1


        x = 0
        while x < 31:
            if histogram[x] is not 0:
                cv2.putText(frame_boxes,'{:2d} = {:d}'.format(x, histogram[x]),
                            (10,50+(x*15)),
                            font,
                            0.35,
                            fontColor,
                            lineType)
            x = x + 1
        
        # Movement 
        if movement == True:
            
            # Timer Tail is always reset at movement
            timerTail = time.time()
                
            if state == STATE_SEARCHING:
                state  = STATE_RECORDING
                
                best_frame = None
                best_weight = 0.0
                acc_objects = set()
                start_time = time.time()
                frame_count = 1
                
                movement_count = 0
                time_str = strftime("%Y-%m-%d_%H.%M.%S", localtime())
                logging.info("Recording started " + time_str)
                out = cv2.VideoWriter("output/" + time_str + ".avi", codec, 6.0, (1280, 720))
                out_boxes = cv2.VideoWriter("output/" + time_str + "_boxes.avi", codec, 6.0, (1280, 720))
                
            movement_count = movement_count + 1
                

        if state == STATE_RECORDING:
                
            frame_count = frame_count + 1
            time_diff = time.time() - timerTail
                
            cv2.putText(frame_boxes,'fps: {:0.2f}'.format(1000000.0 / float(diff)),
                        (10,550),
                        font,
                        fontScale,
                        fontColor,
                        lineType)
            
            cv2.putText(frame_boxes,'frame: ' + str(frame_count),
                        (10,600),
                        font,
                        fontScale,
                        fontColor,
                        lineType)
            
            cv2.putText(frame_boxes,'time since motion: {:0.2f}'.format(time_diff),
                        (10,650),
                        font,
                        fontScale,
                        fontColor,
                        lineType)
                
            # Keep the original frame clean to enable futher postprocessing later
            out.write(frame)
            out_boxes.write(frame_boxes)


            if(weight > best_weight):
                best_weight = weight
                best_frame = frame
                best_weight_display_count = 0

            best_weight_display_count = best_weight_display_count + 1

            # Display snap info for 10 frames
            if best_weight_display_count < 10:
                cv2.putText(frame_boxes,'Best image, weight: {:0.2f}'.format(best_weight),
                            (10,500),
                            font,
                            fontScale,
                            (0,0,255),
                            lineType)
                
                    
            # here we get all the objects found during the whole movie
            acc_objects |= objects

                
            if time_diff > 10.0:
                out.release()
                out_boxes.release()
                state = STATE_SEARCHING

                if movement_count > 5:
                    logging.info("Motion in more than 5 frames detected")
                    
                    db.upload_to_db(best_frame, best_weight, time_str, start_time, frame_count, movement_count, acc_objects)

                else:
                    logging.info("Removing file due to insufficient movment (" + str(movement_count) + ")!")
                    os.remove("output/" + time_str + '.avi')
                    os.remove("output/" + time_str + '_boxes.avi')


            
        server.set_motion_frame(frame_boxes.copy())
    


if __name__ == '__main__':
    
    # construct the argument parse and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", "--num-frames", type=int, default=0,
	            help="# of frames to loop over for FPS test")
    ap.add_argument("-s", "--source", dest='source', type=str, default=None,
	            help="Path to videos input")
    ap.add_argument('-w', '--num-workers', dest='num_workers', type=int,
                        default=1, help='Number of workers.')
    ap.add_argument('-q-size', '--queue-size', dest='queue_size', type=int,
                        default=10, help='Size of the queue.')
    args = vars(ap.parse_args())

    pid = os.getpid()
    p = psutil.Process(pid)    
    
    logging.basicConfig(format='%(asctime)s %(message)s', stream=sys.stdout, level=logging.INFO)    
    logger = multiprocessing.log_to_stderr()
    logger.setLevel(multiprocessing.SUBDEBUG)

    # Multiprocessing: Init input and output Queue and pool of workers
    input_q = Queue(maxsize=args["queue_size"])
    output_q = Queue(maxsize=args["queue_size"])
    pool = Pool(args["num_workers"], worker, (input_q,output_q))

    # Streaming server
    blank_image = np.zeros((1280,720,3), np.uint8)
    server = ThreadedHTTPServer(blank_image, ('0.0.0.0', 9999), CamHandler)
    logging.info("server started")
    httpThread = threading.Thread(target=server.serve_forever)
    httpThread.setDaemon = True
    httpThread.start()

    t = threading.Thread(target=process_frames, args=(output_q, server,))
    t.start()

    rtsp_url = str(os.environ['RTSP_URL'])
    logging.info("Reading RTSP from: " + rtsp_url)
    
    video_capture = cv2.VideoCapture(rtsp_url)
    fn = 0
    while True:
        ret, frame = video_capture.read()
        fn = fn + 1
        if ret:
            server.set_frame(frame)
            if input_q.qsize() > 5:
                tmp = input_q.get()

                # Ok, we allow some dropped frames intially 
                if fn > 40:
                    logging.warning("Dropping one frame at FN = " + str(fn))
                
            input_q.put((fn, frame))
        else:
            logging.warning("Release Camera and stop loop")
            video_capture.release()
            break

    # Sleep some before we exist so we don't keep
    #reconnecting if connection to camera is down
    time.sleep(3)

    logging.error("Exiting! Couldn't read frame from " + rtsp_url)
    p.kill()
    os._exit(1)
