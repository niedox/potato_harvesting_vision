#####################################################
##               Object detection from tensorflow trained model on Realsense Camera                ##
#####################################################
import pyrealsense2 as rs
import numpy as np
import cv2
import tensorflow as tf

from rs_camera import RS_camera
from detection import ObjectDetection
from track_object import ObjectTracker
from pose_computation import Pose
from display import display

#CONSTANTS
MODEL_NAME              = 'mobilenet_igluna_v8'
PATH_TO_FROZEN_GRAPH    = 'trained_model/' + MODEL_NAME + '/frozen_inference_graph.pb'
PATH_TO_LABEL_MAP       = 'label_map.pbtxt'
NUM_CLASSES             = 1
SEG_TYPE                = "edge" #can be "edge", "kmeans"
THRESHOLD               = 0.6

POSE_TYPE               = 0     #0 for PCA, 1 for ellipse fit
DISPLAY                 = 1
EPSILON                 = 60
TRACKING_LIM            = 10 # consecutive frames

#VARIABLES INITIALIZATION
tracking_bool           = 0
consecutive_track       = 0
tracker                 = None
prev_coor               = None
x_mid, y_mid            = None, None


def run_vision():
    camera = RS_camera()
    od = ObjectDetection(PATH_TO_FROZEN_GRAPH, PATH_TO_LABEL_MAP, NUM_CLASSES, SEG_TYPE, THRESHOLD)
    pose = Pose(SEG_TYPE)
    track = ObjectTracker(EPSILON, TRACKING_LIM)

    with od.detection_graph.as_default():
        with tf.compat.v1.Session(graph=od.detection_graph) as sess:
            while True:
                camera.get_frames()

                od.detection(sess, camera)
                track.track_object(od, camera)
                pose.compute_pose(track, camera)
                display(camera, od, track, pose, DISPLAY)
                track.update()

                if cv2.waitKey(25) & 0xFF == ord('q'):
                    cv2.destroyAllWindows()
                    break




if __name__ == '__main__':
    run_vision()






