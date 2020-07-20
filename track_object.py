import numpy as np
from pose_computation import get_dist
from utils import compute_center
from tracking import

class SelectedObject():
    def __init__(self, prev_coor):

        self.prev_coor = prev_coor

        # selected object
        self.box_sel = None
        self.classes_sel = None
        self.scores_sel = None

        # selected object bounding box coordinates (in pixel)
        self.box_coor = [0, 0, 0, 0]  # ymin, xmin, ymax, xmax
        self.box_mid  = [0, 0]  # center of selected box

    def selection(self, od, camera):

        if od.bool:
            dist = get_dist(camera, od)
            idx_sel = np.argmin(dist)
            box_sel, class_sel, score_sel, dist_sel = od.boxes_s[idx_sel], od.classes_s[idx_sel], \
                                                      od.scores_s[idx_sel], dist[idx_sel]

            x_mid, y_mid = compute_center(box_sel)

            if self.prev_coor is None:
                print("HERE")
                tracker = create_tracker(box_sel, image_np)

            elif (np.abs(prev_coor[0] - x_mid) < EPSILON and
                  np.abs(prev_coor[1] - y_mid) < EPSILON):
                tracker = create_tracker(box_sel, image_np)
                consecutive_track = 0

            else:
                FOUND_COHERENT_BOX = 0
                for i in range(len(dist)):
                    x, y, z, x_mid, y_mid = coordinates(boxes_s[i], dist[i], h, w, camera)

                    if (np.abs(prev_coor[0] - x_mid) < EPSILON and
                            np.abs(prev_coor[1] - y_mid) < EPSILON):
                        idx_sel = i
                        FOUND_COHERENT_BOX = 1
                        print("FOUND NEW COHERENT BOX")
                        continue

                if FOUND_COHERENT_BOX:
                    box_sel, class_sel, score_sel, dist_sel = boxes_s[idx_sel], classes_s[idx_sel], \
                                                              scores_s[idx_sel], dist[idx_sel]

                    x, y, z, x_mid, y_mid = coordinates(box_sel, dist_sel, camera)
                    tracker = create_tracker(box_sel, image_np)

                else:
                    box_sel = tracking(tracker, image_np)
                    tracking_bool = 1
                    consecutive_track = consecutive_track + 1

                    box_sel = np.expand_dims(box_sel, 0)
                    dist_sel = get_dist(camera, box_sel)
                    box_sel = np.squeeze(box_sel)

                    x, y, z, x_mid, y_mid = coordinates(box_sel, dist_sel, h, w, camera)

            angle, p_w, p_h = pose(box_sel, dist_sel, ip)




        else:
            if tracker is not None:
                box_sel = tracking(tracker, image_np)
                tracking_bool = 1
                consecutive_track = consecutive_track + 1

                box_sel = np.expand_dims(box_sel, 0)
                dist_sel = get_dist(camera, box_sel)
                box_sel = np.squeeze(box_sel)

                x, y, z, x_mid, y_mid = coordinates(box_sel, dist_sel, camera)
                angle, p_w, p_h = pose(box_sel, dist_sel, ip)