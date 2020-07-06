#####################################################
##               Object detection from tensorflow trained model on Realsense Camera                ##
#####################################################
import pyrealsense2 as rs
import numpy as np
import cv2
import tensorflow as tf
import RS_camera
import dlib

from utils import display_output, draw_orientation
from image_processing import ImageProcessing
from compute_coor import get_dist, get_coor, compute_angle, compute_size



#CONSTANTS
MODEL_NAME              = 'mobilenet_igluna_v8'
PATH_TO_FROZEN_GRAPH    = 'trained_model/' + MODEL_NAME + '/frozen_inference_graph.pb'
PATH_TO_LABEL_MAP       = 'label_map.pbtxt'
NUM_CLASSES             = 1
SEG_TYPE                = "edge" #can be "edge", "kmeans"
THRESHOLD               = 0.7
POSE_TYPE               = 0     #0 for PCA, 1 for ellipse fit
DISPLAY                 = 1
EPSILON                 = 20


def check_for_potato(scores_s):
    """returns a boolean. 0 if no potato are detected, 1 if one or more potato.es are detected."""

    if scores_s.size > 0:
        bool_detection = 1
    else:
        bool_detection = 0

    return bool_detection

def create_tracker(box, image_np):

    h, w = image_np.shape[:2]
    xmin = (box[1] * w).astype(int)
    ymin = (box[0] * h).astype(int)
    xmax = (box[3] * w).astype(int)
    ymax = (box[2] * h).astype(int)

    tracker = dlib.correlation_tracker()
    rect = dlib.rectangle(xmin, ymin, xmax, ymax)
    tracker.start_track(image_np, rect)

    return tracker

def tracking(tracker, image_np):
       # update the tracker and grab the position of the tracked
    # object
    tracker.update(image_np)
    pos = tracker.get_position()

    # unpack the position object
    xmin = int(pos.left())/w
    ymin = int(pos.top())/h
    xmax = int(pos.right())/w
    ymax = int(pos.bottom())/h

    if ymin < 0:
        ymin = 0
    if xmin < 0:
        xmin = 0

    if ymax > 1:
        ymax = 1
    if xmax> 1:
        xmax = 1

    return np.array([ymin, xmin, ymax, xmax])


def coordinates(box, dist, h, w, pipeline):
    """returns the coordinates of the potato detected with the highest certainty"""



    xmin = (box[1] * w).astype(int)
    ymin = (box[0] * h).astype(int)
    xmax = (box[3] * w).astype(int)
    ymax = (box[2] * h).astype(int)

    x_mid = ((xmin + xmax) / 2).astype(int)
    y_mid = ((ymin + ymax) / 2).astype(int)

    if dist.size <= 0:
        return None, None, None, x_mid, y_mid

    x, y, z = get_coor(x_mid, y_mid, dist, pipeline)


    return x, y , z, x_mid, y_mid


def pose(box, dist):
    """returns the orientation, width and height of the potato detected with the highest certainty"""
    box_e = np.expand_dims(box, 0)

    mask_im, box_h, box_w = ip.instance_seg(image_np, box_e)
    box_h, box_w = box_h[0], box_w[0]

    nb_pixels = int(box_h * box_w)
    mask_im_cur = mask_im[0:nb_pixels]
    mask_im_cur = np.reshape(mask_im_cur, (int(box_w), int(box_h)))
    v = ip.principal_axis(mask_im_cur)
    angle = compute_angle(v)
    potato_h, potato_w = compute_size(box, dist, h, w, pipeline)


    return angle, potato_w, potato_h

def display(angle, boxes_s, classes_s, scores_s, category_index, dist):
    if scores_s.size <= 0:
        return

    idx_max = np.argmax(scores_s)
    image_np, colorized_depth, frames = RS_camera.get_frames(pipeline, colorizer)
    h, w = image_np.shape[:2]



    xmin = (boxes_s[:, 1] * w).astype(int)
    ymin = (boxes_s[:, 0] * h).astype(int)
    xmax = (boxes_s[:, 3] * w).astype(int)
    ymax = (boxes_s[:, 2] * h).astype(int)

    x_mid = ((xmin + xmax) / 2).astype(int)
    y_mid = ((ymin + ymax) / 2).astype(int)


    draw_orientation(angle, x_mid[idx_max], y_mid[idx_max], image_np)


if __name__ == '__main__':
    TRACKING = 0
    tracker = None
    prev_coor = None
    x_mid, y_mid = None, None
    ip = ImageProcessing(PATH_TO_FROZEN_GRAPH, PATH_TO_LABEL_MAP, NUM_CLASSES, SEG_TYPE)
    category_index, detection_graph = ip.read_model()
    pipeline, colorizer, depth_scale = RS_camera.start_RS()

    with detection_graph.as_default():
        with tf.compat.v1.Session(graph=detection_graph) as sess:
            while True:
                box_sel = None
                image_np, colorized_depth, frames = RS_camera.get_frames(pipeline, colorizer)
                h, w = image_np.shape[:2]
                boxes, classes, scores = ip.object_detection(detection_graph, sess, image_np)
                boxes_s, classes_s, scores_s = ip.select_objects(boxes, classes, scores, THRESHOLD) #TODO one fct
                #dist = get_dist(frames.get_depth_frame(), depth_scale, boxes_s)
                #dist_clone = dist.copy()

                bool = check_for_potato(scores_s)

                if bool:
                    dist = get_dist(frames.get_depth_frame(), depth_scale, boxes_s)
                    # dist_clone = dist.copy()
                    idx_sel = np.argmin(dist)
                    box_sel, class_sel, score_sel, dist_sel = boxes_s[idx_sel], classes_s[idx_sel], \
                                                             scores_s[idx_sel], dist[idx_sel]

                    x, y, z, x_mid, y_mid = coordinates(box_sel, dist_sel, h, w, pipeline)

                    if prev_coor is None:
                        tracker = create_tracker(box_sel, image_np)

                    elif (np.abs(prev_coor[0] - x_mid) < EPSILON and
                                             np.abs(prev_coor[1] - y_mid) < EPSILON):
                        tracker = create_tracker(box_sel, image_np)
                    else:
                        box_sel = tracking(tracker, image_np)
                        TRACKING = 1
                        print("NOT COHERENT")
                        """FOUND_COHERENT_BOX = 0
                        for i in range(len(dist)):
                            x, y, z, x_mid, y_mid = coordinates(boxes_s[i], dist[i], h, w, pipeline)

                            if (np.abs(prev_coor[0] - x_mid) < EPSILON and
                             np.abs(prev_coor[1] - y_mid) < EPSILON):
                                idx_sel = i
                                FOUND_COHERENT_BOX = 1
                                print("FOUND NEW COHERENT BOX")
                                continue

                        if FOUND_COHERENT_BOX:
                            box_sel, class_sel, score_sel, dist_sel = boxes_s[idx_sel], classes_s[idx_sel], \
                                                                      scores_s[idx_sel], dist[idx_sel]

                            x, y, z, x_mid, y_mid = coordinates(box_sel, dist_sel, h, w, pipeline)
                            tracker = create_tracker(box_sel, image_np)

                        else:
                            box_sel = tracking(tracker, image_np)
                            print("HERE")"""

                    angle, p_w, p_h = pose(box_sel, dist_sel)




                else:
                    if tracker is not None:

                        box_sel = tracking(tracker, image_np)
                        TRACKING = 1
                        box_sel = np.expand_dims(box_sel, 0)
                        dist_sel = get_dist(frames.get_depth_frame(), depth_scale, box_sel)
                        box_sel = np.squeeze(box_sel)

                        x, y, z, x_mid, y_mid = coordinates(box_sel, dist_sel, h, w, pipeline)
                        angle, p_w, p_h = pose(box_sel, dist_sel)


                if DISPLAY:
                    if tracker is not None:
                        org1 = int(box_sel[3] * w)
                        org2 = int(box_sel[0] * h)
                        font = cv2.FONT_HERSHEY_SIMPLEX
                        fontScale = 1 / 2
                        color = (0, 0, 0)
                        thickness = 1
                        xmin = (box_sel[1] * w).astype(int)
                        ymin = (box_sel[0] * h).astype(int)
                        xmax = (box_sel[3] * w).astype(int)
                        ymax = (box_sel[2] * h).astype(int)

                        cv2.putText(image_np, "x: " + str(np.around(100*x, 2)) + " cm", (org1+3, org2 + 15), font,
                                    fontScale, color, thickness=2)
                        cv2.putText(image_np, "y: " + str(np.around(100*y, 2)) + " cm", (org1+3, org2 + 30), font,
                                    fontScale, color, thickness=2)
                        cv2.putText(image_np, "z: " + str(np.around(100*z, 2)) + " cm", (org1+3, org2 + 45), font,
                                    fontScale, color, thickness=2)

                        cv2.putText(colorized_depth, "x: " + str(np.around(100 * x, 2)) + " cm", (org1 + 3, org2 + 15), font,
                                    fontScale, color, thickness=2)
                        cv2.putText(colorized_depth, "y: " + str(np.around(100 * y, 2)) + " cm", (org1 + 3, org2 + 30), font,
                                    fontScale, color, thickness=2)
                        cv2.putText(colorized_depth, "z: " + str(np.around(100 * z, 2)) + " cm", (org1 + 3, org2 + 45), font,
                                    fontScale, color, thickness=2)

                        draw_orientation(angle, x_mid, y_mid, image_np)
                        draw_orientation(angle, x_mid, y_mid, colorized_depth)
                        colorized_depth = display_output(colorized_depth, boxes_s, classes_s, scores_s,
                                                         category_index, dist, "PERCEPTION", idx_sel)
                        image_np = display_output(image_np, boxes_s, classes_s, scores_s, category_index, dist,
                                                  "PERCEPTION", idx_sel)
                        if TRACKING:
                            cv2.rectangle(image_np, (int(box_sel[1]*w), int(box_sel[0]*h)),
                                      (int(box_sel[3]*w), int(box_sel[2]*h)),
                                      (0, 255, 0), thickness=2)
                            cv2.rectangle(colorized_depth, (int(box_sel[1] * w), int(box_sel[0] * h)),
                                      (int(box_sel[3] * w), int(box_sel[2] * h)),
                                      (0, 255, 0), thickness=2)

                        cv2.arrowedLine(image_np, (x_mid, ymax+10 ), (xmax, ymax + 10),
                                        (0, 255, 0), thickness = 2)
                        cv2.arrowedLine(image_np, (x_mid, ymax + 10), (xmin, ymax + 10),
                                        (0, 255, 0), thickness=2)
                        cv2.arrowedLine(colorized_depth, (x_mid, ymax + 10), (xmax, ymax + 10),
                                        (0, 255, 0), thickness=2)
                        cv2.arrowedLine(colorized_depth, (x_mid, ymax + 10), (xmin, ymax + 10),
                                        (0, 255, 0), thickness=2)

                        cv2.arrowedLine(image_np, (xmin - 10, y_mid), (xmin - 10, ymax),
                                        (0, 255, 0), thickness=2)
                        cv2.arrowedLine(image_np, (xmin - 10, y_mid), (xmin - 10, ymin),
                                        (0, 255, 0), thickness=2)
                        cv2.arrowedLine(colorized_depth, (xmin - 10, y_mid), (xmin - 10, ymax),
                                        (0, 255, 0), thickness=2)
                        cv2.arrowedLine(colorized_depth, (xmin - 10, y_mid), (xmin - 10, ymin),
                                        (0, 255, 0), thickness=2)

                        cv2.putText(image_np, str(np.around(100*p_w, 2)) + " cm", (x_mid - 40, ymax + 25), font,
                                    fontScale, color, thickness=2)

                        cv2.putText(image_np, str(np.around(100*p_h, 2)), (xmin - 60, y_mid), font,
                                    fontScale, color, thickness=2)
                        cv2.putText(image_np, "cm", (xmin - 45, y_mid + 30), font,
                                    fontScale, color, thickness=2)

                        cv2.putText(colorized_depth, str(np.around(100*p_w, 2)) + " cm", (x_mid - 40, ymax + 25), font,
                                    fontScale, color, thickness=2)

                        cv2.putText(colorized_depth, str(np.around(100*p_h, 2)), (xmin - 60, y_mid), font,
                                    fontScale, color, thickness=2)
                        cv2.putText(image_np, "cm", (xmin - 45, y_mid + 30), font,
                                    fontScale, color, thickness=2)

                    cv2.imshow("PERCEPTION", np.hstack((image_np, colorized_depth)))




                if cv2.waitKey(25) & 0xFF == ord('q'):
                    cv2.destroyAllWindows()
                    break

                if x_mid is not None:
                    prev_coor = [x_mid, y_mid]
                TRACKING = 0




"""                if bool:

                    idx_sel = np.argmin(dist) #select the closest potato
                    
                    #tracker = create_tracker(box_sel, image_np)

                    if prev_coor is not None:
                        for i in range(len(dist_clone)):
                            if np.abs(prev_coor[0] - x_mid) < EPSILON and np.abs(prev_coor[1] - y_mid) < EPSILON:
                                i = len(dist_clone)
                                box_sel, class_sel, score_sel, dist_sel = boxes_s[idx_sel], classes_s[idx_sel], \
                                                                          scores_s[idx_sel], dist[idx_sel]
                                x, y, z, x_mid, y_mid = coordinates(box_sel, dist_sel, h, w, pipeline)
                                tracker = create_tracker(box_sel, image_np)

                            else:
                                dist_clone[idx_sel] = float("Inf")
                                idx_sel = np.argmin(dist_clone)
                                box_sel, class_sel, score_sel, dist_sel = boxes_s[idx_sel], classes_s[idx_sel], \
                                                                          scores_s[idx_sel], dist[idx_sel]
                                print("SEL", dist_sel)
                                print(idx_sel)
                                x, y, z, x_mid, y_mid = coordinates(box_sel, dist_sel, h, w, pipeline)
                        
                        tracker = create_tracker(box_sel, image_np)

                    #enable tracking if lost potato
                    if dist_clone[idx_sel] == float("Inf"):
                        box_sel = tracking(tracker, image_np)

                    if x_mid is not None:
                        prev_coor = [x_mid, y_mid]

                   #x, y, z, x_mid, y_mid = coordinates(box_sel, dist_sel, h, w, pipeline)


                    angle, potato_w, potato_h = pose(box_sel, dist_sel)

                elif prev_coor is not None:
                    box_sel = tracking(tracker, image_np)
                    #print(box_sel)
                    angle, potato_w, potato_h = pose(box_sel, dist_sel)
                    x, y, z, x_mid, y_mid = coordinates(box_sel, dist_sel, h, w, pipeline)

                    cv2.rectangle(image_np, (int(box_sel[1] * w), int(box_sel[0] * h)),
                                  (int(box_sel[3] * w), int(box_sel[2] * h)), (0, 0, 255), thickness=1)
                    draw_orientation(angle, x_mid, y_mid, image_np)
"""


