import tensorflow as tf
import cv2
import os
import numpy as np
import time

from object_detection.utils import visualization_utils as vis_util
from image_processing import ImageProcessing


#CONSTANTS
MODEL_NAME              = 'mobilenet_igluna_v6'
PATH_TO_FROZEN_GRAPH    = 'trained_model/' + MODEL_NAME + '/frozen_inference_graph.pb'
PATH_TO_LABEL_MAP       = 'label_map.pbtxt'
NUM_CLASSES             = 1
SEG_TYPE                = "edge" #can be "edge", "kmeans"
THRESHOLD               = 0.25
POSE_TYPE               = 0     #0 for PCA, 1 for ellipse fit
IMAGE_DIR           = 'test/'


ip = ImageProcessing(PATH_TO_FROZEN_GRAPH, PATH_TO_LABEL_MAP, NUM_CLASSES, SEG_TYPE)
category_index, detection_graph = ip.read_model()
i = 0

with detection_graph.as_default():
    with tf.compat.v1.Session(graph=detection_graph) as sess:
        for filename in os.listdir(IMAGE_DIR):
            if filename.endswith(".jpg") or filename.endswith(".png"):
                image_np = cv2.imread(os.path.join(IMAGE_DIR, filename))
                #image_np= cv2.resize(image_np, (512, 512))
                #print(image_np.shape)

                start = time.time()
                boxes, classes, scores = ip.object_detection(detection_graph, sess, image_np)
                boxes_s, classes_s, scores_s = ip.select_objects(boxes, classes, scores, THRESHOLD)
                stop = time.time()
                print(stop-start)

                (h, w) = image_np.shape[:2]

                # Visualization of the results of a detection.q
                vis_util.visualize_boxes_and_labels_on_image_array(
                    image_np,
                    boxes_s,
                    classes_s.astype(np.int32),
                    scores_s,
                    category_index,
                    use_normalized_coordinates=True,
                    line_thickness=3,
                    min_score_thresh=0,  # Objects above threshold are already selected before
                )

                cv2.imshow('Detection' + str(i), image_np)

                i = i+1
                if i > 30:
                    break
            else:
                continue


cv2.waitKey(0)
