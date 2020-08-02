import numpy as np
import cv2
import pyrealsense2 as rs

from sklearn.cluster import KMeans




class Pose():
    def __init__(self, seg_type, pose_type):

        # segmentation parameters
        self.seg_type = seg_type
        self.pose_type = pose_type

        # box dimensions (in meters)
        self.box_h = 0
        self.box_w = 0

        # potato pose
        self.position = [0, 0, 0]  # x,y, z (in meters)
        self.angle = 0  # in radian

        #depth data boolean (1 if depth data explotable)
        self.trust_dist = 0

    def get_dist(self, camera, boxes):
        depth_frame = camera.frames.get_depth_frame()
        h, w = camera.h, camera.w

        if len(boxes) == 0:
            dist = []
            return dist

        #get boxes coordinates
        ymin = boxes[:, 0]
        xmin = boxes[:, 1]
        ymax = boxes[:, 2]
        xmax = boxes[:, 3]

        dist = np.zeros(len(xmin))

        # Crop depth data:
        for i in range(len(xmin)):
            #compute central pixel of the boxes
            x = (xmax[i] - xmin[i]) / 2 + xmin[i]
            y = (ymax[i] - ymin[i]) / 2 + ymin[i]

            # min saturation
            if y < 0:
                y = 0
            if x < 0:
                x = 0

            # max saturation
            if y > h:
                y = int(h)
            if x > w:
                x = int(w)

            #get distance
            dist[i] = depth_frame.get_distance(int(x), int(y))
            if dist[i] == 0:
                dist[i] = float('inf')

        return dist



    def image_seg(self, image, boxes_s):

        out_l = [] #linear output array
        box_h, box_w = [], []

        for i in range(boxes_s.shape[0]):
            xmin = boxes_s[i, 0] - 10
            ymin = boxes_s[i, 1] - 10
            xmax = boxes_s[i, 2] + 10
            ymax = boxes_s[i, 3] + 10

            # min saturation
            if ymin < 0:
                ymin = 0
            if xmin < 0:
                xmin = 0

            # crop image
            crop = image[xmin:xmax, ymin:ymax]

            # image segmentation:
            if self.seg_type == "edge":
                gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY) # converting to grayscale
                gray = cv2.bilateralFilter(gray, 11, 17, 17)  # filtering

                if out_l == []:
                    out_l = cv2.Canny(gray, 30, 200) #canny edge detection

                    #linearize image for storage
                    box_h = [out_l.shape[0]]
                    box_w = [out_l.shape[1]]
                    out_l = out_l.reshape(out_l.shape[0] * out_l.shape[1])

                else:
                    edge_im = cv2.Canny(gray, 30, 200) #canny edge detection

                    # linearize image for storage
                    linear_edge_im = edge_im.reshape(edge_im.shape[0] * edge_im.shape[1])
                    box_h = np.append(box_h, edge_im.shape[0])
                    box_w = np.append(box_w, edge_im.shape[1])
                    out_l = np.append(out_l, linear_edge_im)

            elif self.seg_type == "kmeans":
                image = crop
                pic_n = image.reshape(image.shape[0] * image.shape[1], image.shape[2])

                kmeans = KMeans(n_clusters=2, random_state=0).fit(pic_n)
                pic2show = kmeans.cluster_centers_[kmeans.labels_]
                out_cur = pic2show.reshape(image.shape[0], image.shape[1], image.shape[2])

                #linearize output
                linear_out_cur = out_cur.reshape(out_cur.shape[0] * out_cur.shape[1] * out_cur.shape[2])
                box_h = np.append(box_h, (out_cur.shape[0]))
                box_w = np.append(box_w, (out_cur.shape[1]))
                out_l = np.append(out_l, linear_out_cur).astype(int)

        return out_l, box_h, box_w

    def principal_axis(self, crop):

        if self.seg_type == "edge":
            X_row, X_col = np.where(crop > 200)
            X = np.zeros((len(X_row), 2))
            X[:, 0] = X_row
            X[:, 1] = X_col

        elif self.seg_type == "kmeans":
            cv2.imwrite("im3.png", crop)
            X_row, X_col = np.where(crop[:, :, 2] < 80)
            X = np.zeros((len(X_row), 2))
            X[:, 0] = X_row
            X[:, 1] = X_col

        if self.pose_type == 0:
            mean = np.empty((0))
            if len(X) > 0:
                _, eigenvectors, _ = cv2.PCACompute2(X, mean)
                principal_axis = eigenvectors[0, :]
            else:
                principal_axis = [0, 0]

        elif self.pose_type == 1:
            if len(X) < 5:
                return 0
            ellipse = cv2.fitEllipse(np.array(X).astype(int))
            principal_axis = -np.deg2rad(ellipse[2])

        return principal_axis

    def compute_angle(self, axis):
        if self.pose_type == 1:
            return axis

        y = axis[0]
        x = axis[1]

        if x == 0:
            return 0
        else:
            angle = np.arctan(y / x)
        return angle

    def compute_size(self, box, dist, camera):
        depth_frame = camera.frames.get_depth_frame()

        if dist == float('inf') or dist is None:
            return 0, 0

        #get box coordinates
        [ymin, xmin, ymax, xmax] = box
        xmid = (xmin + xmax) / 2
        ymid = (ymin + ymax) /2

        #get corner 3d coordinates
        dist = depth_frame.get_distance(int(xmid), int(ymid))
        top_left = self.point_3D_coor(camera, xmin, ymin, dist)
        bottom_left = self.point_3D_coor(camera, xmin, ymax, dist)
        bottom_right = self.point_3D_coor(camera, xmax, ymax, dist)

        box_height = bottom_left[1] - top_left[1]
        box_width =  bottom_right[0] - bottom_left[0]

        return box_height, box_width

    def box_coordinates(self, track, camera):
        """Computes the real world 3D coordinates of a potato. The camera is considered to be the origine"""
        if track.box_sel is None or track.box_sel == []:
            return 0,0,0

        [ymin, xmin, ymax, xmax] = track.box_sel
        dist = track.dist_sel

        x_mid = ((xmin + xmax) / 2).astype(int)
        y_mid = ((ymin + ymax) / 2).astype(int)

        if dist == []:
            return 0, 0, 0

        # map 2d pixels to 3d coor:
        position = self.point_3D_coor(camera, x_mid, y_mid, dist)

        return position

    def point_3D_coor(self, camera, x, y, dist):

        profile = camera.pipeline.get_active_profile()
        depth_profile = rs.video_stream_profile(profile.get_stream(rs.stream.depth))
        depth_intrinsics = depth_profile.get_intrinsics()
        position = rs.rs2_deproject_pixel_to_point(depth_intrinsics, [x, y], dist)

        return position

    def compute_pose(self, od, track, camera):
        """returns the orientation, width and height of a potato"""

        if od.boxes_s.shape[0] <= 0:
            return

        if not track.dist_sel or track.dist_sel == float('inf'):
            self.trust_dist = 0
        else:
            self.trust_dist = 1

        # image_segmentation
        seg_im, box_h_pix, box_w_pix = self.image_seg(camera.rgb_image, od.boxes_s)
        box_h_pix, box_w_pix = box_h_pix[0], box_w_pix[0]

        nb_pixels = int(box_h_pix * box_w_pix)
        seg_im_cur = seg_im[0:nb_pixels]
        seg_im_cur = np.reshape(seg_im_cur, (int(box_h_pix), int(box_w_pix)))  # reconstruct 2D image

        # compute orientation angle
        v = self.principal_axis(seg_im_cur)
        angle = self.compute_angle(v)

        # compute position and size:
        self.position = self.box_coordinates(track, camera)
        potato_h, potato_w = self.compute_size(track.box_sel, track.dist_sel, camera)
        self.angle, self.box_w, self.box_h = angle, potato_w, potato_h
