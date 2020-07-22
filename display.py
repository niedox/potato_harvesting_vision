import cv2
import numpy as np
from object_detection.utils import visualization_utils as vis_util


FONT      = cv2.FONT_HERSHEY_SIMPLEX
FONTSCALE = 1/2
COLOR = (0,0,0)
THOCKNESS = 1

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


def draw_detection(image_rgb, colorized_depth, od, track):
    ids = (np.ones(len(od.classes_s))).astype(int)


    if not track.tracking_bool:
        color = STANDARD_COLORS.index('Green')
        ids[track.idx_sel] = color

    if len(od.classes_s) > 0:
         # Visualization of the results of a detection.q
         vis_util.visualize_boxes_and_labels_on_image_array(
             image_rgb,
             od.boxes_s,
             od.classes_s.astype(np.int32),
             od.scores_s,
             od.category_index,
             use_normalized_coordinates=False,
             line_thickness=3,
             min_score_thresh=0,  # Objects above threshold are already selected before
             track_ids= ids,
             skip_track_ids = True
         )
         vis_util.visualize_boxes_and_labels_on_image_array(
            colorized_depth,
            od.boxes_s,
            od.classes_s.astype(np.int32),
            od.scores_s,
            od.category_index,
            use_normalized_coordinates=True,
            line_thickness=3,
            min_score_thresh=0,  # Objects above threshold are already selected before
            track_ids=ids,
            skip_track_ids=True
         )
    return image_rgb, colorized_depth

def draw_orientation(track, pose, rgb_image, colorized_depth):
    L = 100 #length of the line in pixels
    x_o, y_o = track.box_mid
    x_line = int(np.cos(pose.angle) * L / 2)
    y_line = int(np.sin(pose.angle) * L / 2)

    cv2.circle(rgb_image, (x_o, y_o), 3, (0, 255, 0), -1)
    cv2.line(rgb_image, (x_o, y_o), (x_o + x_line, y_o + y_line),
             (0, 255, 0), thickness=2)
    cv2.line(rgb_image, (x_o, y_o), (x_o - x_line, y_o - y_line),
             (0, 255, 0), thickness=2)

    cv2.circle(colorized_depth, (x_o, y_o), 3, (0, 255, 0), -1)
    cv2.line(colorized_depth, (x_o, y_o), (x_o + x_line, y_o + y_line),
             (0, 255, 0), thickness=2)
    cv2.line(colorized_depth, (x_o, y_o), (x_o - x_line, y_o - y_line),
             (0, 255, 0), thickness=2)




def display(camera, od, track, pose, DISPLAY):
    if not DISPLAY:
        return

    else:
        image_rgb = camera.rgb_image.copy()
        colorized_depth = camera.colorized_depth.copy()
        x = pose.position[0]
        y = pose.position[1]
        z = pose.position[2]

        if track.box_mid is not None:
            [x_mid, y_mid] = track.box_mid
            print("xmid", x_mid)


        if track.tracker is not None:
            #org1 = int(box_sel[3] * w)
            #org2 = int(box_sel[0] * h)

            xmin = (track.box_sel[1]).astype(int)
            ymin = (track.box_sel[0]).astype(int)
            xmax = (track.box_sel[3]).astype(int)
            ymax = (track.box_sel[2]).astype(int)

            cv2.putText(image_rgb, "x: " + str(np.around(100 * x, 2)) + " cm", (xmax + 3, ymin + 15), FONT,
                        FONTSCALE, COLOR, thickness=2)
            cv2.putText(image_rgb, "y: " + str(np.around(100 * y, 2)) + " cm", (xmax + 3, ymin + 30), FONT,
                        FONTSCALE, COLOR, thickness=2)
            cv2.putText(image_rgb, "z: " + str(np.around(100 * z, 2)) + " cm", (xmax + 3, ymin + 45), FONT,
                        FONTSCALE, COLOR, thickness=2)

            cv2.putText(colorized_depth, "x: " + str(np.around(100 * x, 2)) + " cm", (xmax + 3, ymin + 15),
                        FONT,FONTSCALE, COLOR, thickness=2)
            cv2.putText(colorized_depth, "y: " + str(np.around(100 * y, 2)) + " cm", (xmax + 3, ymin + 30),
                        FONT,FONTSCALE, COLOR, thickness=2)
            cv2.putText(colorized_depth, "z: " + str(np.around(100 * z, 2)) + " cm", (xmax + 3, ymin + 45),
                        FONT,FONTSCALE, COLOR, thickness=2)

            draw_orientation(track, pose, image_rgb, colorized_depth)
            image_rgb, colorized_depth = draw_detection(image_rgb, colorized_depth, od, track)

            if track.tracking_bool:
                cv2.rectangle(image_rgb, (xmin, ymin),
                              (xmax, ymax),
                              (0, 255, 0), thickness=2)
                cv2.rectangle(colorized_depth, (xmin , ymin ),
                              (xmax , ymax ),
                              (0, 255, 0), thickness=2)

                cv2.putText(image_rgb, "TRACKING", (xmin, ymin - 5), FONT,
                            0.7, (0, 0, 255), thickness=1)

            cv2.arrowedLine(image_rgb, (x_mid, ymax + 10), (xmax, ymax + 10),
                            (0, 255, 0), thickness=2)
            cv2.arrowedLine(image_rgb, (x_mid, ymax + 10), (xmin, ymax + 10),
                            (0, 255, 0), thickness=2)
            cv2.arrowedLine(colorized_depth, (x_mid, ymax + 10), (xmax, ymax + 10),
                            (0, 255, 0), thickness=2)
            cv2.arrowedLine(colorized_depth, (x_mid, ymax + 10), (xmin, ymax + 10),
                            (0, 255, 0), thickness=2)

            cv2.arrowedLine(image_rgb, (xmin - 10, y_mid), (xmin - 10, ymax),
                            (0, 255, 0), thickness=2)
            cv2.arrowedLine(image_rgb, (xmin - 10, y_mid), (xmin - 10, ymin),
                            (0, 255, 0), thickness=2)
            cv2.arrowedLine(colorized_depth, (xmin - 10, y_mid), (xmin - 10, ymax),
                            (0, 255, 0), thickness=2)
            cv2.arrowedLine(colorized_depth, (xmin - 10, y_mid), (xmin - 10, ymin),
                            (0, 255, 0), thickness=2)

            cv2.putText(image_rgb, str(np.around(100 * pose.box_w, 2)) + " cm", (x_mid - 40, ymax + 25), FONT,
                        FONTSCALE, COLOR, thickness=2)

            cv2.putText(image_rgb, str(np.around(100 * pose.box_h, 2)), (xmin - 60, y_mid), FONT,
                        FONTSCALE, COLOR, thickness=2)
            cv2.putText(image_rgb, "cm", (xmin - 45, y_mid + 30), FONT,
                        FONTSCALE, COLOR, thickness=2)


            cv2.putText(colorized_depth, str(np.around(100 * pose.box_w, 2)) + " cm", (x_mid - 40, ymax + 25),
                        FONT,
                        FONTSCALE, COLOR, thickness=2)

            cv2.putText(colorized_depth, str(np.around(100 * pose.box_h, 2)), (xmin - 60, y_mid), FONT,
                        FONTSCALE, COLOR, thickness=2)
            cv2.putText(image_rgb, "cm", (xmin - 45, y_mid + 30), FONT,
                        FONTSCALE, COLOR, thickness=2)


        cv2.imshow("PERCEPTION", np.hstack((image_rgb, colorized_depth)))

