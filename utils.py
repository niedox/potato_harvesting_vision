import numpy as np
import cv2

from object_detection.utils import visualization_utils as vis_util

STANDARD_COLORS = [
    'AliceBlue', 'Chartreuse', 'Aqua', 'Aquamarine', 'Azure', 'Beige', 'Bisque',
    'BlanchedAlmond', 'BlueViolet', 'BurlyWood', 'CadetBlue', 'AntiqueWhite',
    'Chocolate', 'Coral', 'CornflowerBlue', 'Cornsilk', 'Crimson', 'Cyan',
    'DarkCyan', 'DarkGoldenRod', 'DarkGrey', 'DarkKhaki', 'DarkOrange',
    'DarkOrchid', 'DarkSalmon', 'DarkSeaGreen', 'DarkTurquoise', 'DarkViolet',
    'DeepPink', 'DeepSkyBlue', 'DodgerBlue', 'FireBrick', 'FloralWhite',
    'ForestGreen', 'Fuchsia', 'Gainsboro', 'GhostWhite', 'Gold', 'GoldenRod',
    'Salmon', 'Tan', 'HoneyDew', 'HotPink', 'IndianRed', 'Ivory', 'Khaki',
    'Lavender', 'LavenderBlush', 'LawnGreen', 'LemonChiffon', 'LightBlue',
    'LightCoral', 'LightCyan', 'LightGoldenRodYellow', 'LightGray', 'LightGrey',
    'LightGreen', 'LightPink', 'LightSalmon', 'LightSeaGreen', 'LightSkyBlue',
    'LightSlateGray', 'LightSlateGrey', 'LightSteelBlue', 'LightYellow', 'Lime',
    'LimeGreen', 'Linen', 'Magenta', 'MediumAquaMarine', 'MediumOrchid',
    'MediumPurple', 'MediumSeaGreen', 'MediumSlateBlue', 'MediumSpringGreen',
    'MediumTurquoise', 'MediumVioletRed', 'MintCream', 'MistyRose', 'Moccasin',
    'NavajoWhite', 'OldLace', 'Olive', 'OliveDrab', 'Orange', 'OrangeRed',
    'Orchid', 'PaleGoldenRod', 'PaleGreen', 'PaleTurquoise', 'PaleVioletRed',
    'PapayaWhip', 'PeachPuff', 'Peru', 'Pink', 'Plum', 'PowderBlue', 'Purple',
    'Red', 'RosyBrown', 'RoyalBlue', 'SaddleBrown', 'Green', 'SandyBrown',
    'SeaGreen', 'SeaShell', 'Sienna', 'Silver', 'SkyBlue', 'SlateBlue',
    'SlateGray', 'SlateGrey', 'Snow', 'SpringGreen', 'SteelBlue', 'GreenYellow',
    'Teal', 'Thistle', 'Tomato', 'Turquoise', 'Violet', 'Wheat', 'White',
    'WhiteSmoke', 'Yellow', 'YellowGreen'
]


def draw_detection(image_np, boxes, classes, scores, category_index, dist, idx_sel, tracking_bool):
    (h, w) = image_np.shape[:2]

    ids = (np.ones(len(dist))).astype(int)

    if not tracking_bool:
        color = STANDARD_COLORS.index('Green')
        ids[idx_sel] = color

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
             track_ids= ids,
             skip_track_ids = True
         )

         """for i in range(len(dist)):
           coor = (int(boxes[i,1]*w), int(boxes[i, 0]*h))
           cv2.putText(image_np, "dist: " + str(round(dist[i], 2)) + " [m]", coor, cv2.FONT_HERSHEY_SIMPLEX, 0.35,
                       (255, 255, 255))"""

    return image_np

def draw_orientation(angle, x_o, y_o, image):
    L = 100 #length of the line in pixels


    cv2.circle(image, (x_o, y_o), 3, (0, 255, 0), -1)

    x_line = int(np.cos(angle)*L/2)
    y_line = int(np.sin(angle)*L/2)

    cv2.line(image, (x_o, y_o), (x_o + x_line, y_o + y_line),
             (0, 255, 0), thickness=2)

    cv2.line(image, (x_o, y_o), (x_o - x_line, y_o - y_line),
             (0, 255, 0), thickness=2)





