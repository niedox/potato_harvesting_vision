#####################################################
##               Object detection from tensorflow trained model on Realsense Camera                ##
#####################################################
import pyrealsense2 as rs
import numpy as np
import cv2
import tensorflow as tf
import RS_camera

from utils import display_output
from image_processing import ImageProcessing


#CONSTANTS
MODEL_NAME              = 'mobilenet_v1_2'
PATH_TO_FROZEN_GRAPH    = 'trained_model/' + MODEL_NAME + '/frozen_inference_graph.pb'
PATH_TO_LABEL_MAP       = 'label_map.pbtxt'
NUM_CLASSES             = 1
SEG_TYPE                = "edge" #can be "edge", "kmeans"
THRESHOLD               = 0.5


"""# Patch the location of gfile
tf.gfile = tf.io.gfile

INPUT_SOURCE = 'realsense'  #webcam or realsense
MODEL_NAME = 'mobilenet_v1_2'
# path to the frozen graph:
PATH_TO_FROZEN_GRAPH = 'trained_model/' + MODEL_NAME + '/frozen_inference_graph.pb'
# path to the label map
# number of classes


COLORS = np.random.uniform(0, 255, size=(NUM_CLASSES, 3))
#SKIP = 0"""


def process_vision():
    ip = ImageProcessing(PATH_TO_FROZEN_GRAPH, PATH_TO_LABEL_MAP, NUM_CLASSES, SEG_TYPE)
    category_index, detection_graph = ip.read_model()
    pipeline, colorizer, depth_scale = RS_camera.start_RS()

    with detection_graph.as_default():
        with tf.compat.v1.Session(graph=detection_graph) as sess:
            while True:
                image_np, colorized_depth, frames = RS_camera.get_frames(pipeline, colorizer)

                # i = i+1
                # if i > SKIP:
                # i = 0

                boxes, classes, scores = ip.object_detection(detection_graph, sess, image_np)
                boxes_s, classes_s, scores_s = ip.select_objects(boxes, classes, scores, THRESHOLD)
                dist = RS_camera.get_dist(frames.get_depth_frame(), depth_scale, boxes_s)

                mask_im, box_h, box_w = ip.instance_seg(colorized_depth, boxes_s)
                display_output(image_np, boxes_s, classes_s, scores_s, category_index, dist, 'RGB')
                display_output(colorized_depth, boxes_s, classes_s, scores_s, category_index, dist, 'Depth')
                # display_output(mask_im, boxes_s, classes_s, scores_s, category_index, dist, 'Mask')
                if mask_im != []:
                    buff = 0
                    for i in range(boxes_s.shape[0]):
                        nb_pixels = box_h[i] * box_w[i]
                        mask_im_cur = mask_im[buff:(buff + nb_pixels)]
                        mask_im_cur = np.reshape(mask_im_cur, (box_w[i], box_h[i]))
                        cv2.imshow("mask " + str(i), mask_im_cur)
                        buff = buff + nb_pixels

                if cv2.waitKey(25) & 0xFF == ord('q'):
                    cv2.destroyAllWindows()
                    break



if __name__ == '__main__':
    process_vision()