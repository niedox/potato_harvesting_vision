"""Object selection and tracking"""

import numpy as np
import dlib
from vision_lib.utils import compute_center


class ObjectTracker():
    def __init__(self, epsilon, tracking_lim, ripeness_thres):

        self.prev_coor = None
        self.epsilon = epsilon
        self.tracking_lim = tracking_lim

        self.tracker = None
        self.consecutive_track = 0
        self.tracking_bool = 0

        # selected object

        self.box_sel = None
        self.classes_sel = None
        self.scores_sel = None
        self.box_mid  = None  # center of selected box

        self.dist_sel = None
        self.idx_sel = None

        self.ripeness_thres = ripeness_thres

    def update(self):
        if self.box_mid is not None:
            self.prev_coor = self.box_mid
        self.tracking_bool = 0
        if self.consecutive_track >= self.tracking_lim:
            self.__init__(self.epsilon, self.tracking_lim, self.ripeness_thres)

    def create_tracker(self, box, camera):
        """Create a dlib tracker object on the detection box given in input"""
        xmin = (box[1]).astype(int)
        ymin = (box[0]).astype(int)
        xmax = (box[3]).astype(int)
        ymax = (box[2]).astype(int)

        tracker = dlib.correlation_tracker()
        rect = dlib.rectangle(xmin, ymin, xmax, ymax)
        tracker.start_track(camera.rgb_image, rect)

        return tracker


    def track_object(self, od, camera, pose):


        #Ripeness Filtering_
        self.ripeness_filter(camera, od, pose)

        #Tracking
        if od.bool:

            #selection based on distance
            dist = pose.get_dist(camera, od.boxes_s)
            idx_sel = np.argmin(dist)
            self.box_sel, self.class_sel, self.score_sel, self.dist_sel = od.boxes_s[idx_sel], od.classes_s[idx_sel], \
                                                      od.scores_s[idx_sel], dist[idx_sel]
            self.idx_sel = idx_sel
            self.box_mid = compute_center(self.box_sel)

            #if no selection previous frames
            if self.prev_coor is None:
                self.tracker = self.create_tracker(self.box_sel, camera)

            #if selection coherent
            elif (np.abs(self.prev_coor[0] - self.box_mid[0]) < self.epsilon and
                  np.abs(self.prev_coor[1] - self.box_mid[1]) < self.epsilon):
                print("coherent")
                self.tracker = self.create_tracker(self.box_sel, camera)
                self.consecutive_track = 0

            #looking for coherent box in detected objects
            else:
                FOUND_COHERENT_BOX = 0
                for i in range(len(dist)):
                    self.box_mid = compute_center(self.box_sel)
                    if (np.abs(self.prev_coor[0] - self.box_mid[0]) < self.epsilon and
                            np.abs(self.prev_coor[1] - self.box_mid[1]) < self.epsilon):
                        idx_sel = i
                        self.idx_sel = idx_sel
                        FOUND_COHERENT_BOX = 1
                        continue

                if FOUND_COHERENT_BOX:
                    print("coherent")
                    self.box_sel, self.class_sel, self.score_sel, self.dist_sel = od.boxes_s[idx_sel], od.classes_s[idx_sel], \
                                                                                  od.scores_s[idx_sel], dist[idx_sel]

                    self.box_mid = compute_center(self.box_sel)
                    self.tracker = self.create_tracker(self.box_sel, camera)

                else:
                    print("NOT coherent")

                    self.box_sel = self.tracking(self.tracker, camera) #track

                    self.tracking_bool = 1
                    self.consecutive_track = self.consecutive_track + 1

                    box_sel_e = np.expand_dims(self.box_sel, 0)
                    self.dist_sel = pose.get_dist(camera, box_sel_e)
                    self.box_mid = compute_center(self.box_sel)

        #tracking if no ripe potato detected:
        else:
            if self.tracker is not None:
                self.box_sel = self.tracking(self.tracker, camera)
                self.tracking_bool = 1
                self.consecutive_track = self.consecutive_track + 1
                box_sel_e = np.expand_dims(self.box_sel, 0)
                self.dist_sel =pose.get_dist(camera, box_sel_e)
                self.box_mid = compute_center(self.box_sel)

    def ripeness_filter(self, camera, od, pose):

        if od.bool:
            dist = pose.get_dist(camera, od.boxes_s)
            idx_sel = np.argmin(dist)
            box_h, box_w = pose.compute_size(od.boxes_s[idx_sel, :], dist[idx_sel], camera)

            # Loop in detected objects to find a ripe potato:
            while box_h * box_w < self.ripeness_thres and min(dist) < float('inf'):
                dist[idx_sel] = float('inf')
                idx_sel = np.argmin(dist)
                box_h, box_w = pose.compute_size(od.boxes_s[idx_sel, :], dist[idx_sel], camera)

            if min(dist) == float('inf'):
                od.bool = 0

    def tracking(self, tracker, camera):
        """update the tracker and returns the position of the tracked object"""
        h, w = camera.h, camera.w
        tracker.update(camera.rgb_image)
        pos = tracker.get_position()

        # unpack the position object
        xmin = int(pos.left())
        ymin = int(pos.top())
        xmax = int(pos.right())
        ymax = int(pos.bottom())


        # min saturation
        if ymin < 0:
            ymin = 0
        if xmin < 0:
            xmin = 0

        # max saturation
        if ymax > h:
            ymax = int(h)
        if xmax > w:
            xmax = int(w)

        return np.array([ymin, xmin, ymax, xmax])
