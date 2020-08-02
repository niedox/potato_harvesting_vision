"""Tests the accuracy and precision of the orientation estimation methods"""

import os
import tensorflow as tf
import cv2
import time
import numpy as np

import _init_paths
from pathlib import Path
from vision_lib.detection import ObjectDetection
from vision_lib.pose_computation import Pose

from object_detection.utils import visualization_utils as vis_util



currentPath = os.path.dirname(os.path.realpath(__file__))
workingPath = str(Path(currentPath).parents[0])

MODEL_NAME              = 'ssd300_mobilenet'
PATH_TO_FROZEN_GRAPH    = workingPath + '/trained_model/' + MODEL_NAME + '/frozen_inference_graph.pb'
PATH_TO_LABEL_MAP       = workingPath + '/label_map.pbtxt'
NUM_CLASSES             = 1
THRESHOLD               = 0.5


#CHOSE POSE ESTIMATION METHODE:
SEG_TYPE                = "kmeans" #can be "edge", "kmeans"
POSE_TYPE               = 1     #0 for PCA, 1 for ellipse fit


def compute_orientation(pose, image, box):

    mask_im, box_h_pix, box_w_pix = pose.instance_seg(image, box)
    box_h_pix, box_w_pix = box_h_pix[0], box_w_pix[0]

    if SEG_TYPE == "kmeans":
        nb_pixels = int(box_h_pix * box_w_pix * 3)
        mask_im_cur = mask_im[0:nb_pixels]
        mask_im_cur = np.reshape(mask_im_cur, (int(box_h_pix), int(box_w_pix), 3))
    else:
        nb_pixels = int(box_h_pix * box_w_pix)
        mask_im_cur = mask_im[0:nb_pixels]
        mask_im_cur = np.reshape(mask_im_cur, (int(box_h_pix), int(box_w_pix)))


    #cv2.imwrite("im2.png", mask_im_cur)

    v = pose.principal_axis(mask_im_cur, image)
    angle = pose.compute_angle(v)

    return angle


def draw_detection(image, box, class_, score, category_index):


     # Visualization of the results of a detection.q
     vis_util.visualize_boxes_and_labels_on_image_array(
         image,
         np.expand_dims(box, 0),
         np.expand_dims(class_.astype(np.int32), 0),
         np.expand_dims(score, 0),
         category_index,
         use_normalized_coordinates=False,
         line_thickness=3,
         min_score_thresh=0  # Objects above threshold are already selected before
     )

     return image

def draw_orientation(angle, image, box):
    L = 100 #length of the line in pixels

    ymin = box[0]
    xmin = box[1]
    ymax = box[2]
    xmax = box[3]

    x_o, y_o = int((xmax + xmin)/2), int((ymax + ymin)/2)
    x_line = int(np.cos(angle) * L / 2)
    y_line = int(np.sin(angle) * L / 2)

    cv2.circle(image, (x_o, y_o), 3, (0, 255, 0), -1)
    cv2.line(image, (x_o, y_o), (x_o + x_line, y_o + y_line),
             (0, 255, 0), thickness=2)
    cv2.line(image, (x_o, y_o), (x_o - x_line, y_o - y_line),
             (0, 255, 0), thickness=2)

    return image

def store_detections(od):
    detection_list, classes_list, scores_list, cat_list = [], [], [], []
    directory = currentPath + "/orientation_test/rgb"

    for sub_dir in sorted(os.listdir(directory)):
        for filename in sorted(os.listdir(directory + "/" + sub_dir)):
            image = cv2.imread(directory  + "/" + sub_dir + "/" + filename)
            print(directory  + "/" + sub_dir + "/" + filename)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            od.detection(sess, image)
            detection_list = np.append(detection_list, od.boxes_s[0])
            classes_list  = np.append(classes_list, od.classes_s[0])
            scores_list = np.append(scores_list, od.scores_s[0])
            cat_list = np.append(cat_list, od.category_index)

    return detection_list, classes_list, scores_list, cat_list

m = 0
n = 0

def compute_errors(directory, storage_list, true_angle, boxes, classes_list, scores_list, cat_list):
    global n
    global m
    for filename in sorted(os.listdir(directory)):
        print(filename)
        image = cv2.imread(directory + filename)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        box= np.array(boxes[n:n+4]).astype(int)

        angle = compute_orientation(pose, image, np.expand_dims(box, 0))
        image = draw_detection(image, box, classes_list[m], scores_list[m], cat_list[m])
        image = draw_orientation(angle, image, box)
        cv2.imshow("im", image)
        cv2.imwrite("im1.jpg", cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

        error = -true_angle-angle

        print("ERR b", np.rad2deg(error))
        if error > 0:
            error = error % (np.pi)
            if error > (np.pi/2):
                error = np.pi - error
        else:
            error = - (-error % (np.pi))
            if error < (-np.pi/2):
                error = np.pi + error

        print("ERR", np.rad2deg(error))
        storage_list = np.append(storage_list, error)
        qcv2.waitKey()
        cv2.destroyAllWindows()

        n = n+4
        m = m+1
        print("n = ", n)


    return storage_list


od = ObjectDetection(PATH_TO_FROZEN_GRAPH, PATH_TO_LABEL_MAP, NUM_CLASSES, SEG_TYPE, THRESHOLD)
pose = Pose(SEG_TYPE, POSE_TYPE)

error_high_lum = []
error_low_lum  = []
error_high_lum_d = []
error_low_lum_d  = []



with od.detection_graph.as_default():
    with tf.compat.v1.Session(graph=od.detection_graph) as sess:

        detection_list, classes_list, scores_list, cat_list = store_detections(od)
        start_rgb = time.time()

        error_high_lum = compute_errors(currentPath + "/orientation_test/rgb/0_high_rgb/", error_high_lum, 0, detection_list, classes_list, scores_list, cat_list)
        error_low_lum = compute_errors(currentPath + "/orientation_test/rgb/0_low_rgb/", error_low_lum, 0, detection_list, classes_list, scores_list, cat_list)
        error_high_lum = compute_errors(currentPath + "/orientation_test/rgb/135_high_rgb/", error_high_lum,
                                        3 * np.pi / 4, detection_list, classes_list, scores_list, cat_list)
        error_low_lum = compute_errors(currentPath + "/orientation_test/rgb/135_low_rgb/", error_low_lum, 3 * np.pi / 4,
                                       detection_list, classes_list, scores_list, cat_list)
        error_high_lum = compute_errors(currentPath + "/orientation_test/rgb/45_high_rgb/", error_high_lum, np.pi/4, detection_list, classes_list, scores_list, cat_list)
        error_low_lum = compute_errors(currentPath + "/orientation_test/rgb/45_low_rgb/", error_low_lum, np.pi / 4, detection_list, classes_list, scores_list, cat_list)
        error_high_lum = compute_errors(currentPath + "/orientation_test/rgb/90_high_rgb/", error_high_lum, np.pi/2, detection_list, classes_list, scores_list, cat_list)
        error_low_lum = compute_errors(currentPath + "/orientation_test/rgb/90_low_rgb/", error_low_lum, np.pi / 2, detection_list, classes_list, scores_list, cat_list)
        stop_rgb = time.time()
        avg_error_high_lum = np.mean(error_high_lum)
        avg_error_low_lum = np.mean(error_low_lum)

        std_error_high_lum = np.std(error_high_lum)
        std_error_low_lum = np.std(error_low_lum)

        m = 0
        n= 0
        start_d = time.time()
        error_high_lum_d = compute_errors(currentPath + "/orientation_test/depth/0_high_depth/", error_high_lum_d, 0,
                                        detection_list, classes_list, scores_list, cat_list)
        error_low_lum_d = compute_errors(currentPath + "/orientation_test/depth/0_low_depth/", error_low_lum_d, 0,
                                       detection_list, classes_list, scores_list, cat_list)
        error_high_lum_d = compute_errors(currentPath + "/orientation_test/depth/135_high_depth/", error_high_lum_d,
                                        3 * np.pi / 4, detection_list, classes_list, scores_list, cat_list)
        error_low_lum_d = compute_errors(currentPath + "/orientation_test/depth/135_low_depth/", error_low_lum_d, 3 * np.pi / 4,
                                       detection_list, classes_list, scores_list, cat_list)
        error_high_lum_d = compute_errors(currentPath + "/orientation_test/depth/45_high_depth/", error_high_lum_d, np.pi / 4,
                                        detection_list, classes_list, scores_list, cat_list)
        error_low_lum_d = compute_errors(currentPath + "/orientation_test/depth/45_low_depth/", error_low_lum_d, np.pi / 4,
                                       detection_list, classes_list, scores_list, cat_list)
        error_high_lum_d = compute_errors(currentPath + "/orientation_test/depth/90_high_depth/", error_high_lum_d, np.pi / 2,
                                        detection_list, classes_list, scores_list, cat_list)
        error_low_lum_d = compute_errors(currentPath + "/orientation_test/depth/90_low_depth/", error_low_lum_d, np.pi / 2,
                                       detection_list, classes_list, scores_list, cat_list)
        stop_d = time.time()
        avg_error_high_lum_d = np.mean(error_high_lum_d)


        abs_err = np.mean(np.abs(error_high_lum))
        print("AAAAAAAAAAAAa", np.rad2deg(abs_err))

        abs_err = np.mean(np.abs(error_low_lum))
        print("BBBBBBBBBBBBb", np.rad2deg(abs_err))


        abs_err = np.mean(np.abs(error_high_lum_d))
        print("CCCCCCCCCCCC", np.rad2deg(abs_err))

        abs_err = np.mean(np.abs(error_low_lum_d))
        print("DDDDDDDDDDDDD", np.rad2deg(abs_err))


        avg_error_low_lum_d= np.mean(error_low_lum_d)

        std_error_high_lum_d = np.std(error_high_lum_d)
        std_error_low_lum_d = np.std(error_low_lum_d)

        tot_error = np.append(error_high_lum, error_low_lum)
        tot_error_d = np.append(error_high_lum_d, error_low_lum_d)

        print("high", np.rad2deg(avg_error_high_lum))
        print("low", np.rad2deg(avg_error_low_lum))

        print("high d", np.rad2deg(avg_error_high_lum_d))
        print("low d", np.rad2deg(avg_error_low_lum_d))

        print("std high", np.rad2deg(std_error_high_lum))
        print("std low", np.rad2deg(std_error_low_lum))

        print("std high d", np.rad2deg(std_error_high_lum_d))
        print("std low d", np.rad2deg(std_error_low_lum_d))

        print("avg time rgb: ", (stop_rgb-start_rgb)/39)
        print("avg time depth: ", (stop_d-start_d)/39)

        print("tot std", np.rad2deg(np.std(tot_error)))
        print("tot std d", np.rad2deg(np.std(tot_error_d)))