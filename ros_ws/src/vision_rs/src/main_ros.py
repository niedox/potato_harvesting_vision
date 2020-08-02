#! /usr/bin/env python

"""Perception algorithm for ROS environment"""

import cv2
import tensorflow as tf
import os
import rospy

import _init_paths
from vision_rs.msg import Vision
from vision_lib.rs_camera import RS_camera
from vision_lib.detection import ObjectDetection
from vision_lib.track_object import ObjectTracker
from vision_lib.pose_computation import Pose
from vision_lib.display import display
from pathlib import Path


currentPath = os.path.dirname(os.path.realpath(__file__))
workingPath = str(Path(currentPath).parents[3])



"""CONSTANTS"""

#Object Detection:
MODEL_NAME              = 'ssd300_mobilenet'
PATH_TO_FROZEN_GRAPH    = workingPath + '/trained_model/' + MODEL_NAME + '/frozen_inference_graph.pb'
PATH_TO_LABEL_MAP       = workingPath + '/label_map.pbtxt'
NUM_CLASSES             = 1
THRESHOLD               = 0.99 #detection threshold


#Pose Estimation:
SEG_TYPE                = "edge" #can be "edge", "kmeans"
POSE_TYPE               = 0     #0 for PCA, 1 for ellipse fit
DISPLAY                 = 1

#Tracking
EPSILON                 = 30 #coherence limit
TRACKING_LIM            = 3  # consecutive frames

#VARIABLES INITIALIZATION
tracking_bool           = 0
consecutive_track       = 0
tracker                 = None
prev_coor               = None
x_mid, y_mid            = None, None

def init_node():
    global pub, rate, msg

    rospy.init_node("Vision")
    pub = rospy.Publisher('/Vision', Vision, queue_size=10)
    rate = rospy.Rate(10)
    msg = Vision()

def publish(od, pose):
    msg.bool_detection = od.bool
    msg.bool_depth     = pose.trust_dist
    msg.x, msg.y, msg.z = pose.position
    msg.height, msg.width = pose.box_h, pose.box_h
    msg.angle = pose.angle

    rospy.loginfo(msg)
    pub.publish(msg)
    rate.sleep()


def run_vision():

    #initialize classes
    camera = RS_camera()
    od = ObjectDetection(PATH_TO_FROZEN_GRAPH, PATH_TO_LABEL_MAP, NUM_CLASSES, SEG_TYPE, THRESHOLD)
    pose = Pose(SEG_TYPE)
    track = ObjectTracker(EPSILON, TRACKING_LIM)

    with od.detection_graph.as_default():
        with tf.compat.v1.Session(graph=od.detection_graph) as sess:
            while not rospy.is_shutdown():
                camera.get_frames()

                od.detection(sess, camera.rgb_image)
                track.track_object(od, camera)
                pose.compute_pose(track, camera)
                display(camera, od, track, pose, DISPLAY)

                track.update()

                publish(od, pose)


                if cv2.waitKey(25) & 0xFF == ord('q'):
                    cv2.destroyAllWindows()
                    break




if __name__ == '__main__':
    init_node()
    run_vision()






