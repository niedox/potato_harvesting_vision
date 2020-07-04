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
THRESHOLD               = 0.5
POSE_TYPE               = 0     #0 for PCA, 1 for ellipse fit

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
                dist = get_dist(frames.get_depth_frame(), depth_scale, boxes_s)
                mask_im, box_h, box_w = ip.instance_seg(image_np, boxes_s)

                if mask_im != []:
                    buff = 0
                    for i in range(boxes_s.shape[0]):
                        nb_pixels = int(box_h[i] * box_w[i])

                        mask_im_cur = mask_im[buff:(buff + nb_pixels)]
                        mask_im_cur = np.reshape(mask_im_cur, (int(box_w[i]), int(box_h[i])))
                        if POSE_TYPE == 0:
                            h, w = image_np.shape[:2]

                            v = ip.principal_axis(mask_im_cur)

                            #mask_im_cur = gray2rgb(mask_im_cur)
                            #yo = mask_im_cur.shape[0]
                            #cv2.line(mask_im_cur, (0, yo), (int(100*v[0][1]), yo + int(100*v[0][0])),
                            #        (0, 0, 255), thickness=2)
                            xo = (boxes_s[i, 1] * w).astype(int)
                            yo = (boxes_s[i, 0] * h).astype(int)
                            x_mid = int((xo + boxes_s[i, 3] * w)/2)
                            y_mid = int((yo + boxes_s[i, 2] * h)/2)

                            angle = compute_angle(v)
                            draw_orientation(angle, x_mid, y_mid, image_np)
                            x, y, z = get_coor(x_mid, y_mid, dist[i], pipeline)

                            potato_h, potato_w = compute_size(boxes_s[i, :], dist[i], h, w, pipeline)

                            print(potato_h, potato_w)

                            #ow("mask " + str(i), mask_im_cur)

                        elif POSE_TYPE == 1:
                            _, binary_im = cv2.threshold(mask_im_cur,  0.5, 255, 0)
                            #cnts = cv2.findContours(binary_im, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                            #cnts = grab_contours(cnts)
                            #cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:10]
                            mask_im_cur = cv2.cvtColor(mask_im_cur, cv2.COLOR_GRAY2BGR)
                            pt_x, pt_y, _ = np.where(mask_im_cur>200)
                            pts = np.zeros((len(pt_x), 2))
                            pts[:,0] = pt_x
                            pts[:,1] = pt_y
                            pts = pts.astype(int)
                            if pts.shape[0]>5:
                                el = cv2.fitEllipse(pts)
                                cv2.ellipse(mask_im_cur, el, (255, 0, 255), 2)
                                x0 = (boxes_s[i, 1] * image_np.shape[1]).astype(int)
                                y0 = (boxes_s[i, 0] * image_np.shape[0]).astype(int)


                                el = ((el[0][0] + x0, el[0][1] + y0), el[1], el[2])
                                cv2.ellipse(image_np, el,
                                         (255, 0, 255), thickness=2)
                            #cv2.drawContours(mask_im_cur, cnts, -1, (0, 255, 0), 3)
                            #cv2.imshow("mask " + str(i), mask_im_cur)
                        buff = buff + nb_pixels

                display_output(image_np, boxes_s, classes_s, scores_s, category_index, dist, 'RGB')
                display_output(colorized_depth, boxes_s, classes_s, scores_s, category_index, dist, 'Depth')



                if cv2.waitKey(25) & 0xFF == ord('q'):
                    cv2.destroyAllWindows()
                    break



process_vision()