#####################################################
##               Object detection from tensorflow trained model on Realsense Camera                ##
#####################################################
import pyrealsense2 as rs
import numpy as np
import cv2
import tensorflow as tf
import RS_camera

from utils import display_output, draw_orientation
from image_processing import ImageProcessing
from compute_coor import get_dist, get_coor, compute_angle, compute_size



#CONSTANTS
MODEL_NAME              = 'mobilenet_igluna_v6'
PATH_TO_FROZEN_GRAPH    = 'trained_model/' + MODEL_NAME + '/frozen_inference_graph.pb'
PATH_TO_LABEL_MAP       = 'label_map.pbtxt'
NUM_CLASSES             = 1
SEG_TYPE                = "edge" #can be "edge", "kmeans"
THRESHOLD               = 0.8
POSE_TYPE               = 0     #0 for PCA, 1 for ellipse fit
DISPLAY                 = 1


def check_for_potato(scores_s):
    """returns a boolean. 0 if no potato are detected, 1 if one or more potato.es are detected."""

    if scores_s.size > 0:
        bool_detection = 1
    else:
        bool_detection = 0

    return bool_detection

def coordinates(box, dist, h, w, pipeline):
    """returns the coordinates of the potato detected with the highest certainty"""

    if scores_s.size <= 0:
        return None, None, None

    xmin = (box[1] * w).astype(int)
    ymin = (box[0] * h).astype(int)
    xmax = (box[3] * w).astype(int)
    ymax = (box[2] * h).astype(int)

    x_mid = ((xmin + xmax) / 2).astype(int)
    y_mid = ((ymin + ymax) / 2).astype(int)

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

    display_output(image_np, boxes_s, classes_s, scores_s, category_index, dist, 'RGB')
    display_output(colorized_depth, boxes_s, classes_s, scores_s, category_index, dist, 'Depth')


if __name__ == '__main__':

    ip = ImageProcessing(PATH_TO_FROZEN_GRAPH, PATH_TO_LABEL_MAP, NUM_CLASSES, SEG_TYPE)
    category_index, detection_graph = ip.read_model()
    pipeline, colorizer, depth_scale = RS_camera.start_RS()

    with detection_graph.as_default():
        with tf.compat.v1.Session(graph=detection_graph) as sess:
            while True:
                image_np, colorized_depth, frames = RS_camera.get_frames(pipeline, colorizer)
                h, w = image_np.shape[:2]
                boxes, classes, scores = ip.object_detection(detection_graph, sess, image_np)
                boxes_s, classes_s, scores_s = ip.select_objects(boxes, classes, scores, THRESHOLD) #TODO one fct

                dist = get_dist(frames.get_depth_frame(), depth_scale, boxes_s)

                bool = check_for_potato(scores_s)
                if not bool:
                    continue

                idx_max = np.argmax(scores_s)
                box_max, class_max, score_max, dist_max = boxes_s[idx_max], classes_s[idx_max], \
                                                scores_s[idx_max], dist[idx_max]


                x, y, z, x_mid, y_mid = coordinates(box_max, dist_max, h, w, pipeline)
                angle, potato_w, potato_h = pose(box_max, dist_max)

                if DISPLAY:
                    draw_orientation(angle, x_mid, y_mid, image_np)
                    display_output(image_np, boxes_s, classes_s, scores_s, category_index, dist, "pipopapo")

                    print("x:", x, "y", y, "z", z)
                    print("h", potato_h, "w", potato_w)
                if cv2.waitKey(25) & 0xFF == ord('q'):
                    cv2.destroyAllWindows()
                    break






