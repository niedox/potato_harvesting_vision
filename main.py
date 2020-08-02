#####################################################
##               Object detection and Pose Estimation of Potatoes on Realsense Camera D415                ##
#####################################################
import cv2
import os
import tensorflow as tf

from vision_lib.rs_camera import RS_camera
from vision_lib.detection import ObjectDetection
from vision_lib.track_object import ObjectTracker
from vision_lib.pose_computation import Pose
from vision_lib.display import display


currentPath = os.path.dirname(os.path.realpath(__file__))


#CONSTANTS#

#Object Detection:
MODEL_NAME              = 'ssd512_mobilenet'
PATH_TO_FROZEN_GRAPH    = currentPath + '/trained_model/' + MODEL_NAME + '/frozen_inference_graph.pb'
PATH_TO_LABEL_MAP       = currentPath + '/label_map.pbtxt'
NUM_CLASSES             = 1
THRESHOLD               = 0.99

#Pose Estimation:
SEG_TYPE                = "edge" #can be "edge", "kmeans"
POSE_TYPE               = 0     #0 for PCA, 1 for ellipse fit

#Tracking
RIPENESS_THRES          = 0
EPSILON                 = 300 #proximity threshold
TRACKING_LIM            = 10 # consecutive frames

#Display
DISPLAY                 = 1


def run_vision():
    camera = RS_camera()
    od = ObjectDetection(PATH_TO_FROZEN_GRAPH, PATH_TO_LABEL_MAP, NUM_CLASSES, SEG_TYPE, THRESHOLD)
    pose = Pose(SEG_TYPE, POSE_TYPE)
    track = ObjectTracker(EPSILON, TRACKING_LIM, RIPENESS_THRES)

    with od.detection_graph.as_default():
        with tf.compat.v1.Session(graph=od.detection_graph) as sess:
            while True:
                camera.get_frames()

                od.detection(sess, camera.rgb_image)
                track.track_object(od, camera, pose)
                pose.compute_pose(od, track, camera)

                display(camera, od, track, pose, DISPLAY)
                track.update()


                if cv2.waitKey(25) & 0xFF == ord('q'):
                    cv2.destroyAllWindows()
                    break


if __name__ == '__main__':
    run_vision()






