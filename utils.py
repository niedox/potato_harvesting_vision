import numpy as np
import cv2

from object_detection.utils import visualization_utils as vis_util


def display_output(image_np, boxes, classes, scores, category_index, dist, name):
    (h, w) = image_np.shape[:2]

    if len(dist) > 0:
         # Visualization of the results of a detection.q
         vis_util.visualize_boxes_and_labels_on_image_array(
             image_np,
             boxes,
             classes.astype(np.int32),
             scores,
             category_index,
             use_normalized_coordinates=True,
             line_thickness=3,
             min_score_thresh=0,  # Objects above threshold are already selected before
         )
         for i in range(len(dist)):
           coor = (int(boxes[i,1]*w), int(boxes[i, 0]*h))
           cv2.putText(image_np, "dist: " + str(round(dist[i], 2)) + " [m]", coor, cv2.FONT_HERSHEY_SIMPLEX, 0.35,
                       (255, 255, 255))

    cv2.imshow(name, image_np)

def draw_orientation(angle, x_o, y_o, image):
    L = 100 #length of the line in pixels


    cv2.circle(image, (x_o, y_o), 3, (0, 0, 255), -1)

    x_line = int(np.cos(angle)*L/2)
    y_line = int(np.sin(angle)*L/2)

    cv2.line(image, (x_o, y_o), (x_o + x_line, y_o + y_line),
             (0, 0, 255), thickness=2)

    cv2.line(image, (x_o, y_o), (x_o - x_line, y_o - y_line),
             (0, 0, 255), thickness=2)





