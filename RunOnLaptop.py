#!/usr/bin/env python


#####################################################
##               Object detection from tensorflow trained model on Realsense Camera                ##
#####################################################
import pyrealsense2 as rs
import numpy as np
import cv2
import tensorflow as tf
import dlib
import rospy


from utils import draw_detection, draw_orientation
from detection import ImageProcessing
from compute_coor import get_dist, get_coor, compute_angle, compute_size

# CONSTANTS
MODEL_NAME = 'mobilenet_igluna_v8'
PATH_TO_FROZEN_GRAPH = 'trained_model/' + MODEL_NAME + '/frozen_inference_graph.pb'
PATH_TO_LABEL_MAP = 'label_map.pbtxt'
NUM_CLASSES = 1
SEG_TYPE = "edge"  # can be "edge", "kmeans"
THRESHOLD = 0.6

POSE_TYPE = 0  # 0 for PCA, 1 for ellipse fit
DISPLAY = 1
EPSILON = 60
TRACKING_LIM = 3  # consecutive frames

# VARIABLES INIT
prev_coor = None
tracking_bool = 0
consecutive_track = 0
tracker = None
x_mid, y_mid = None, None


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
    xmin = int(pos.left()) / w
    ymin = int(pos.top()) / h
    xmax = int(pos.right()) / w
    ymax = int(pos.bottom()) / h

    if ymin < 0:
        ymin = 0
    if xmin < 0:
        xmin = 0

    if ymax > 1:
        ymax = 1
    if xmax > 1:
        xmax = 1

    return np.array([ymin, xmin, ymax, xmax])





def pose_b(box):
    """returns the orientation, width and height of the potato detected with the highest certainty"""
    box_e = np.expand_dims(box, 0)

    mask_im, box_h, box_w = ip.instance_seg(image_np, box_e)
    box_h, box_w = box_h[0], box_w[0]

    nb_pixels = int(box_h * box_w)
    mask_im_cur = mask_im[0:nb_pixels]
    mask_im_cur = np.reshape(mask_im_cur, (int(box_w), int(box_h)))
    v = ip.principal_axis(mask_im_cur)
    angle = compute_angle(v)

    return angle


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

    # draw_orientation(angle, x_mid[idx_max], y_mid[idx_max], image_np)

def mid_coordinates(box, h, w):
    """returns the coordinates of the potato detected with the highest certainty"""



    xmin = (box[1] * w).astype(int)
    ymin = (box[0] * h).astype(int)
    xmax = (box[3] * w).astype(int)
    ymax = (box[2] * h).astype(int)

    x_mid = ((xmin + xmax) / 2).astype(int)
    y_mid = ((ymin + ymax) / 2).astype(int)



    return x_mid, y_mid



if __name__ == '__main__':
    ip = ImageProcessing(PATH_TO_FROZEN_GRAPH, PATH_TO_LABEL_MAP, NUM_CLASSES, SEG_TYPE)
    category_index, detection_graph = ip.read_model()
    cap = cv2.VideoCapture(0)

    with detection_graph.as_default():
        with tf.compat.v1.Session(graph=detection_graph) as sess:
            while True:
                box_sel = None
                _, image_np = cap.read()
                h, w = image_np.shape[:2]
                boxes, classes, scores = ip.object_detection(detection_graph, sess, image_np)
                boxes_s, classes_s, scores_s = ip.select_objects(boxes, classes, scores, THRESHOLD)  # TODO one fct

                bool = check_for_potato(scores_s)

                if bool:
                    idx_sel = np.argmax(classes_s)

                    box_sel, class_sel, score_sel = boxes_s[idx_sel], classes_s[idx_sel], \
                                                              scores_s[idx_sel]
                    x_mid, y_mid = mid_coordinates(box_sel, h, w)

                    if prev_coor is None:
                        print("HERE")
                        tracker = create_tracker(box_sel, image_np)

                    elif (np.abs(prev_coor[0] - x_mid) < EPSILON and
                          np.abs(prev_coor[1] - y_mid) < EPSILON):
                        tracker = create_tracker(box_sel, image_np)
                        consecutive_track = 0

                    else:
                        FOUND_COHERENT_BOX = 0
                        for i in range(len(classes_s)):
                            x_mid, y_mid = mid_coordinates(box_sel, h, w)

                            if (np.abs(prev_coor[0] - x_mid) < EPSILON and
                                    np.abs(prev_coor[1] - y_mid) < EPSILON):
                                idx_sel = i
                                FOUND_COHERENT_BOX = 1
                                print("FOUND NEW COHERENT BOX")
                                continue

                        if FOUND_COHERENT_BOX:
                            box_sel, class_sel, score_sel = boxes_s[idx_sel], classes_s[idx_sel], \
                                                                      scores_s[idx_sel]
                            x_mid, y_mid = mid_coordinates(box_sel, h, w)
                            tracker = create_tracker(box_sel, image_np)

                        else:
                            box_sel = tracking(tracker, image_np)
                            tracking_bool = 1
                            consecutive_track = consecutive_track + 1

                            box_sel = np.expand_dims(box_sel, 0)
                            box_sel = np.squeeze(box_sel)

                            x_mid, y_mid = mid_coordinates(box_sel, h, w)
                            angle = pose_b(box_sel)

                    angle = pose_b(box_sel)





                else:
                    if tracker is not None:
                        box_sel = tracking(tracker, image_np)
                        tracking_bool = 1
                        consecutive_track = consecutive_track + 1

                        box_sel = np.expand_dims(box_sel, 0)
                        box_sel = np.squeeze(box_sel)

                        x_mid, y_mid = mid_coordinates(box_sel, h, w)
                        angle = pose_b(box_sel)

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



                        # draw_orientation(angle, x_mid, y_mid, image_np)
                        # draw_orientation(angle, x_mid, y_mid, colorized_depth)

                        image_np = draw_detection(image_np, boxes_s, classes_s, scores_s, category_index, [0],
                                                  idx_sel, tracking_bool)
                        if tracking_bool:
                            cv2.rectangle(image_np, (int(box_sel[1] * w), int(box_sel[0] * h)),
                                          (int(box_sel[3] * w), int(box_sel[2] * h)),
                                          (0, 255, 0), thickness=2)

                            cv2.putText(image_np, "TRACKING", (xmin, ymin - 5), font,
                                        0.7, (0, 0, 255), thickness=1)

                        cv2.arrowedLine(image_np, (x_mid, ymax + 10), (xmax, ymax + 10),
                                        (0, 255, 0), thickness=2)
                        cv2.arrowedLine(image_np, (x_mid, ymax + 10), (xmin, ymax + 10),
                                        (0, 255, 0), thickness=2)


                        cv2.arrowedLine(image_np, (xmin - 10, y_mid), (xmin - 10, ymax),
                                        (0, 255, 0), thickness=2)
                        cv2.arrowedLine(image_np, (xmin - 10, y_mid), (xmin - 10, ymin),
                                        (0, 255, 0), thickness=2)

                        cv2.putText(image_np, "cm", (xmin - 45, y_mid + 30), font,
                                    fontScale, color, thickness=2)


                        cv2.putText(image_np, "cm", (xmin - 45, y_mid + 30), font,
                                    fontScale, color, thickness=2)

                cv2.imshow("PERCEPTION", image_np)

                if cv2.waitKey(25) & 0xFF == ord('q'):
                    cv2.destroyAllWindows()
                    break

                if x_mid is not None:
                    prev_coor = [x_mid, y_mid]

                tracking_bool = 0

                if consecutive_track >= TRACKING_LIM:
                    consecutive_track = 0
                    tracker = None
                    prev_coor = None
                    x_mid, y_mid = None, None
                    print("YES")

