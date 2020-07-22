import tensorflow as tf
import cv2
import os
import numpy as np
import time

from object_detection.utils import visualization_utils as vis_util
from vision_lib import ObjectDetection


#CONSTANTS
MODEL_NAME              = 'faster_rcnn_v4'
PATH_TO_FROZEN_GRAPH    = 'trained_model/' + MODEL_NAME + '/frozen_inference_graph.pb'
PATH_TO_LABEL_MAP       = 'label_map.pbtxt'
NUM_CLASSES             = 1
SEG_TYPE                = "edge" #can be "edge", "kmeans"
THRESHOLD               = 0.2
POSE_TYPE               = 0     #0 for PCA, 1 for ellipse fit
IMAGE_DIR               = 'evaluation/test/'
DETECTION_FILE          = 'evaluation/detection_faster_rcnn/'


ip = ObjectDetection(PATH_TO_FROZEN_GRAPH, PATH_TO_LABEL_MAP, NUM_CLASSES, SEG_TYPE, THRESHOLD)
ip.read_model()
i = 0

with ip.detection_graph.as_default():
    with tf.compat.v1.Session(graph=ip.detection_graph) as sess:
        print(sorted(os.listdir(IMAGE_DIR)))
        for filename in sorted(os.listdir(IMAGE_DIR)):
            if filename.endswith(".jpg") or filename.endswith(".png"):
                image_np = cv2.imread(os.path.join(IMAGE_DIR, filename))
                image_np = cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)

                #image_np= cv2.resize(image_np, (512, 512))

                start = time.time()
                ip.detection(sess, image_np)
                boxes_s, classes_s, scores_s = ip.boxes_s, ip.classes_s, ip.scores_s

                stop = time.time()
                #print(stop-start)

                (h, w) = image_np.shape[:2]

                # Visualization of the results of a detection.q
                vis_util.visualize_boxes_and_labels_on_image_array(
                    image_np,
                    boxes_s,
                    classes_s.astype(np.int32),
                    scores_s,
                    ip.category_index,
                    use_normalized_coordinates=False,
                    line_thickness=3,
                    min_score_thresh=0,  # Objects above threshold are already selected before
                )
                cv2.imshow('Detection' + str(i), image_np)


                #Write detections in txt files
                f = open(DETECTION_FILE + "file" + str(i) + ".txt", "x")
                LIST = [1, 0, 3, 2]  # xmin, ymin, xmax, ymax

                for j in range(len(classes_s)):
                    f.write("potato ")
                    f.write(str(scores_s[j]))
                    for k, list in enumerate(LIST):
                        f.write(" " + str(boxes_s[j][list]))
                    f.write("\n")


                i = i+1
            else:
                continue




if cv2.waitKey(25) & 0xFF == ord('q'):
    cv2.destroyAllWindows()