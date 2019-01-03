import os
import cv2
import numpy as np
import tensorflow as tf
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util
import time
import imutils
import struct
import six
import collections
from matplotlib import colors


# Path to frozen detection graph. This is the actual model that is used for the object detection.
PATH_TO_CKPT = 'model/frozen_inference_graph.pb'

# List of the strings that is used to add correct label for each box.
PATH_TO_LABELS = 'model/mscoco_label_map.pbtxt'
face_cascade = cv2.CascadeClassifier('model/haarcascade_frontalface_alt2.xml')

NUM_CLASSES = 90

# Loading label map
label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES,
                                                            use_display_name=True)
category_index = label_map_util.create_category_index(categories)

width = 1280
height = 720 

def get_important_objects(
        boxes,
        classes,
        scores,
        category_index,
        min_score_thresh=.5):

    ret = set()
    for i in range(boxes.shape[0]):
        if scores is not None and scores[i] > min_score_thresh:
            if classes[i] in category_index.keys():
                class_name = category_index[classes[i]]['name']
                ret.add(class_name)        

    return ret

def standard_colors():
    colors = [
        'AliceBlue', 'Chartreuse', 'Aqua', 'Aquamarine', 'Azure', 'Beige', 'Bisque',
        'BlanchedAlmond', 'BlueViolet', 'BurlyWood', 'CadetBlue', 'AntiqueWhite',
        'Chocolate', 'Coral', 'CornflowerBlue', 'Cornsilk', 'Crimson', 'Cyan',
        'DarkCyan', 'DarkGoldenRod', 'DarkGrey', 'DarkKhaki', 'DarkOrange',
        'DarkOrchid', 'DarkSalmon', 'DarkSeaGreen', 'DarkTurquoise', 'DarkViolet',
        'DeepPink', 'DeepSkyBlue', 'DodgerBlue', 'FireBrick', 'FloralWhite',
        'ForestGreen', 'Fuchsia', 'Gainsboro', 'GhostWhite', 'Gold', 'GoldenRod',
        'Salmon', 'Tan', 'HoneyDew', 'HotPink', 'IndianRed', 'Ivory', 'Khaki',
        'Lavender', 'LavenderBlush', 'LawnGreen', 'LemonChiffon', 'LightBlue',
        'LightCoral', 'LightCyan', 'LightGoldenRodYellow', 'LightGray', 'LightGrey',
        'LightGreen', 'LightPink', 'LightSalmon', 'LightSeaGreen', 'LightSkyBlue',
        'LightSlateGray', 'LightSlateGrey', 'LightSteelBlue', 'LightYellow', 'Lime',
        'LimeGreen', 'Linen', 'Magenta', 'MediumAquaMarine', 'MediumOrchid',
        'MediumPurple', 'MediumSeaGreen', 'MediumSlateBlue', 'MediumSpringGreen',
        'MediumTurquoise', 'MediumVioletRed', 'MintCream', 'MistyRose', 'Moccasin',
        'NavajoWhite', 'OldLace', 'Olive', 'OliveDrab', 'Orange', 'OrangeRed',
        'Orchid', 'PaleGoldenRod', 'PaleGreen', 'PaleTurquoise', 'PaleVioletRed',
        'PapayaWhip', 'PeachPuff', 'Peru', 'Pink', 'Plum', 'PowderBlue', 'Purple',
        'Red', 'RosyBrown', 'RoyalBlue', 'SaddleBrown', 'Green', 'SandyBrown',
        'SeaGreen', 'SeaShell', 'Sienna', 'Silver', 'SkyBlue', 'SlateBlue',
        'SlateGray', 'SlateGrey', 'Snow', 'SpringGreen', 'SteelBlue', 'GreenYellow',
        'Teal', 'Thistle', 'Tomato', 'Turquoise', 'Violet', 'Wheat', 'White',
        'WhiteSmoke', 'Yellow', 'YellowGreen'
    ]
    return colors


def color_name_to_rgb():
    colors_rgb = []
    for key, value in colors.cnames.items():
        colors_rgb.append((key, struct.unpack('BBB', bytearray.fromhex(value.replace('#', '')))))
    return dict(colors_rgb)
    
    
def draw_boxes_and_labels(
        boxes,
        classes,
        scores,
        category_index,
        instance_masks=None,
        keypoints=None,
        max_boxes_to_draw=20,
        min_score_thresh=.5,
        agnostic_mode=False):
    """Returns boxes coordinates, class names and colors
    Args:
      boxes: a numpy array of shape [N, 4]
      classes: a numpy array of shape [N]
      scores: a numpy array of shape [N] or None.  If scores=None, then
        this function assumes that the boxes to be plotted are groundtruth
        boxes and plot all boxes as black with no classes or scores.
      category_index: a dict containing category dictionaries (each holding
        category index `id` and category name `name`) keyed by category indices.
      instance_masks: a numpy array of shape [N, image_height, image_width], can
        be None
      keypoints: a numpy array of shape [N, num_keypoints, 2], can
        be None
      max_boxes_to_draw: maximum number of boxes to visualize.  If None, draw
        all boxes.
      min_score_thresh: minimum score threshold for a box to be visualized
      agnostic_mode: boolean (default: False) controlling whether to evaluate in
        class-agnostic mode or not.  This mode will display scores but ignore
        classes.
    """
    # Create a display string (and color) for every box location, group any boxes
    # that correspond to the same location.
    box_to_display_str_map = collections.defaultdict(list)
    box_to_color_map = collections.defaultdict(str)
    box_to_instance_masks_map = {}
    box_to_keypoints_map = collections.defaultdict(list)
    if not max_boxes_to_draw:
        max_boxes_to_draw = boxes.shape[0]
    for i in range(min(max_boxes_to_draw, boxes.shape[0])):
        if scores is None or scores[i] > min_score_thresh:
            box = tuple(boxes[i].tolist())
            if instance_masks is not None:
                box_to_instance_masks_map[box] = instance_masks[i]
            if keypoints is not None:
                box_to_keypoints_map[box].extend(keypoints[i])
            if scores is None:
                box_to_color_map[box] = 'black'
            else:
                if not agnostic_mode:
                    if classes[i] in category_index.keys():
                        class_name = category_index[classes[i]]['name']
                    else:
                        class_name = 'N/A'
                    display_str = '{}: {}%'.format(
                        class_name,
                        int(100 * scores[i]))
                else:
                    display_str = 'score: {}%'.format(int(100 * scores[i]))
                box_to_display_str_map[box].append(display_str)
                if agnostic_mode:
                    box_to_color_map[box] = 'DarkOrange'
                else:
                    box_to_color_map[box] = standard_colors()[
                        classes[i] % len(standard_colors())]
                    
    # Store all the coordinates of the boxes, class names and colors
    color_rgb = color_name_to_rgb()
    rect_points = []
    class_names = []
    class_colors = []
    for box, color in six.iteritems(box_to_color_map):
        ymin, xmin, ymax, xmax = box
        rect_points.append(dict(ymin=ymin, xmin=xmin, ymax=ymax, xmax=xmax))
        class_names.append(box_to_display_str_map[box])
        class_colors.append(color_rgb[color.lower()])
    return rect_points, class_names, class_colors

def is_within_box(point, x, y):

    # We only look in upper 1/2 of the box for faces
    if x > point['xmin'] and x < point['xmax']:
        if y > point['ymin'] and y < (point['ymax']/2):
            return True
    return False

def detect_objects(image_np, sess, detection_graph):
    # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
    image_np_expanded = np.expand_dims(image_np, axis=0)
    image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')

    # Each box represents a part of the image where a particular object was detected.
    boxes = detection_graph.get_tensor_by_name('detection_boxes:0')

    # Each score represent how level of confidence for each of the objects.
    # Score is shown on the result image, together with the class label.
    scores = detection_graph.get_tensor_by_name('detection_scores:0')
    classes = detection_graph.get_tensor_by_name('detection_classes:0')
    num_detections = detection_graph.get_tensor_by_name('num_detections:0')

    # Actual detection.
    (boxes, scores, classes, num_detections) = sess.run(
        [boxes, scores, classes, num_detections],
        feed_dict={image_tensor: image_np_expanded})


    important_objects = get_important_objects(
        np.squeeze(boxes),
        np.squeeze(classes).astype(np.int32),
        np.squeeze(scores),
        category_index) 

    # Visualization of the results of a detection.
    rect_points, class_names, class_colors = draw_boxes_and_labels(
                boxes=np.squeeze(boxes),
                classes=np.squeeze(classes).astype(np.int32),
                scores=np.squeeze(scores),
                category_index=category_index,
                min_score_thresh=.5
            )
    return important_objects, dict(rect_points=rect_points, class_names=class_names, class_colors=class_colors)



def get_objects_and_faces(objs, data, frame_boxes, grayscale_frame):

    
    rec_points = data['rect_points']
    class_names = data['class_names']
    class_colors = data['class_colors']
    
    faces = []
    if 'person' in objs:
        
        faces = face_cascade.detectMultiScale(
            grayscale_frame,
            scaleFactor=1.1,
            minNeighbors=2
        )
    weight = 0.0
    # Draw the tensorflow objects and check for faces
    for point, name, color in zip(rec_points, class_names, class_colors):
        cv2.rectangle(frame_boxes, (int(point['xmin'] * width), int(point['ymin'] * height)),
                      (int(point['xmax'] * width), int(point['ymax'] * height)), color, 3)
        cv2.rectangle(frame_boxes, (int(point['xmin'] * width), int(point['ymin'] * height)),
                      (int(point['xmin'] * width) + len(name[0]) * 6,
                       int(point['ymin'] * height) - 10), color, -1, cv2.LINE_AA)
        cv2.putText(frame_boxes, name[0], (int(point['xmin'] * width), int(point['ymin'] * height)), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 0), 1)
        if name[0].startswith('person:'):

            # We add some weight if there are persons in the image
            weight = weight + 0.01

            for (x, y, w, h) in faces:
                # Draw a rectangle around the faces
                cv2.rectangle(frame_boxes, (int(x*2.56), int(y*2.56)), (int(x*2.56) + int(w*2.56), int(y*2.56) + int(h*2.56)), (255, 0, 0), 2)
                
                # Calculate extra weight (the more faces and area size (within person rectangle))  
                middle = x+w/2
                m = float(middle)/float(500)
                top = y + 5
                t = float(top)/float(280)

                if is_within_box(point, m, t):
                    weight = weight + 2.0
                    area = (float(w)/float(500)) * (float(h)/float(280))
                    weight = weight + area    

                # extra weight if the posistion is 'good' i.e. up the stairs
                xpos = point['xmax'] - point['xmin']
                xdiff = abs(xpos-0.35)
                
                ylen = point['ymax'] - point['ymin']
                ydiff = abs(ylen-0.8)
                
                weight = weight + (1.0 - (xdiff+ydiff))

    return weight, frame_boxes



def worker(input_q, output_q):
    # Load a (frozen) Tensorflow model into memory.
    detection_graph = tf.Graph()
    with detection_graph.as_default():
        od_graph_def = tf.GraphDef()
        with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
            serialized_graph = fid.read()
            od_graph_def.ParseFromString(serialized_graph)
            tf.import_graph_def(od_graph_def, name='')
        sess = tf.Session(graph=detection_graph)

    prev_frame = None

    while True:
        frame_number, frame = input_q.get()

        start = time.time()
        
        # this is the frame we are going to alter
        frame_boxes = frame.copy()
        weight = 0.0

        # resize the frame, convert it to grayscale, and blur it
        frame_small = imutils.resize(frame, width=500)
        # OpenCV wants BGR and tensorflow wants RGB
        frame_rgb = cv2.cvtColor(frame_small, cv2.COLOR_BGR2RGB)

        #motion, frame_boxes, prev_frame = get_motion(grayscale_frame, frame_boxes, prev_frame)

        grayscale_frame = cv2.cvtColor(frame_small, cv2.COLOR_BGR2GRAY)
        grayscale_frame = cv2.GaussianBlur(grayscale_frame, (21, 21), 0)
        
        # if the first frame is None, initialize it
        if prev_frame is None:
            prev_frame = grayscale_frame
            
        motion = False

        # compute the absolute difference between current and the first frame
        delta_frame = cv2.absdiff(prev_frame, grayscale_frame)
    
        # compute the threshold frame
        frame_thres = cv2.threshold(delta_frame, 25, 255, cv2.THRESH_BINARY)[1]
        
        # dilate the thresholded frame, then find contours
        frame_thres = cv2.dilate(frame_thres, None, iterations=3)
        contours = cv2.findContours(frame_thres.copy(), cv2.RETR_EXTERNAL,
                                    cv2.CHAIN_APPROX_SIMPLE)
        contours = contours[0] if imutils.is_cv2() else contours[1]
        
        scale = 1280.0/500.0
        
        # Now we have diffed the frame so set it to prev
        prev_frame = grayscale_frame
            
        # loop through the contours we found
        for c in contours:
            # ignore small contours
            if cv2.contourArea(c) > 200:
                motion = True
            
                # draw rectangle for the contour
                (x, y, w, h) = cv2.boundingRect(c)


                # but we need to normalized small to normal frame size
                cv2.rectangle(frame_boxes, (int(x*scale), int(y*scale)),
                              (int(x*scale) + int(w*scale),
                               int(y*scale) + int(h*scale)),
                              (0, 0, 255), 2)

                # draw the thres frame to indicate which frames pass the 200 "small contours" threshold
                cv2.rectangle(frame_thres, (x, y), (x + w, y + h), (255, 255, 255), 2)

        
        objs, data = detect_objects(frame_rgb, sess, detection_graph)

        weight, frame_boxes = get_objects_and_faces(objs, data, frame_boxes, grayscale_frame)

        output_q.put((frame_number, dict(frame_boxes=frame_boxes, frame_thres=frame_thres, motion=motion, important_objects=objs, weight=weight, processing_time=(time.time()-start))))
        
        #print "Task time " + str(int((time.time() - start) *1000)) +  "ms face count = " + str(face_count) 

    sess.close()

