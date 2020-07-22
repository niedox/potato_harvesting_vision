import numpy as np
import cv2
import pyrealsense2 as rs


def get_dist(camera, boxes):
    depth_frame = camera.frames.get_depth_frame()
    print(boxes)

    if len(boxes) == 0:
        dist = []
        return dist
    ymin = boxes[:, 0]
    xmin = boxes[:, 1]
    ymax = boxes[:, 2]
    xmax = boxes[:, 3]

    dist = np.zeros(len(xmin))
    # Crop depth data:
    for i in range(len(xmin)):
        x = (xmax[i] - xmin[i]) / 2 + xmin[i]
        y = (ymax[i] - ymin[i]) / 2 + ymin[i]

        """depth = depth[xmin[i]:xmax[i], ymin[i]:ymax[i]].astype(float)
        # Get data scale from the device and
        depth = depth * depth_scale

        #dist[i], _, _, _ = cv2.minMaxLoc(depth)
        dist[i], _, _, _ = cv2.mean(depth)"""
        dist[i] = depth_frame.get_distance(int(x), int(y))

    return dist


class Pose():
    def __init__(self, seg_type):

        # segmentation parameters
        self.seg_type = seg_type
        self.kernel = np.array([np.array([1, 1, 1]), np.array([1, -8, 1]), np.array([1, 1, 1])])

        #box dimensions (in meters)
        self.box_h = 0
        self.box_w = 0

        #potato position
        self.position = [0, 0, 0] #x,y, z (in meters)
        self.angle    = 0      #in radian

    def compute_pose(self, track, camera):
        """returns the orientation, width and height of a potato"""
        if track.box_sel is None:
            return

        box_e = np.expand_dims(track.box_sel, 0)
        mask_im, box_h_pix, box_w_pix = self.instance_seg(camera, box_e)
        box_h_pix, box_w_pix = box_h_pix[0], box_w_pix[0]

        nb_pixels = int(box_h_pix * box_w_pix)
        mask_im_cur = mask_im[0:nb_pixels]
        mask_im_cur = np.reshape(mask_im_cur, (int(box_w_pix), int(box_h_pix)))
        v = self.principal_axis(mask_im_cur)
        angle = self.compute_angle(v)

        self.position= self.coordinates(track, camera)

        potato_h, potato_w = self.compute_size(track, camera)
        self.angle, self.box_w, self.box_h = angle, potato_w, potato_h





    def compute_angle(self, axis):
        y = axis[0]
        x = axis[1]

        if x == 0:
            return 0
        else:
            angle = np.arctan(y / x)
        return angle

    def compute_size(self, track, camera):
        h, w = camera.h, camera.w
        [xmid, ymid] = track.box_mid
        [ymin, xmin, ymax, xmax] = track.box_sel

        if track.dist_sel == 0 or None:
            return 0, 0


        [xmid_m, ymid_m, _]= self.position

        xmid_wrt_center = xmid - w / 2
        ymid_wrt_center = ymid - h / 2

        ratio_x = xmid_wrt_center / xmid_m
        ratio_y = ymid_wrt_center / ymid_m

        box_height = (ymax - ymin) / ratio_y
        box_width = (xmax - xmin) / ratio_x

        return box_height, box_width

    def instance_seg(self, camera, boxes_s):
        image = camera.rgb_image

        (h, w) = image.shape[:2]
        out_l = []
        box_h, box_w = [], []
        # crop image
        for i in range(boxes_s.shape[0]):
            xmin = boxes_s[i, 0]
            ymin = boxes_s[i, 1]
            xmax = boxes_s[i, 2]
            ymax = boxes_s[i, 3]
            crop = image[xmin:xmax, ymin:ymax]

            # edge detection
            if self.seg_type == "edge":
                # converting to grayscale
                # gray = rgb2gray(crop)
                gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
                gray = cv2.bilateralFilter(gray, 11, 17, 17)
                # cv2.imshow("GRAY", gray)

                if out_l == []:
                    # out_l = ndimage.convolve(gray, self.kernel, mode='reflect')
                    out_l = cv2.Canny(gray, 30, 200)
                    out_l = out_l.reshape(out_l.shape[0] * out_l.shape[1])
                    box_h = [(ymax - ymin)]
                    box_w = [(xmax - xmin)]
                else:
                    # edge_im = ndimage.convolve(gray, self.kernel, mode='reflect')
                    edge_im = cv2.Canny(gray, 30, 200)
                    linear_edge_im = edge_im.reshape(edge_im.shape[0] * edge_im.shape[1])
                    box_h = np.append(box_h, (ymax - ymin))
                    box_w = np.append(box_w, (xmax - xmin))
                    out_l = np.append(out_l, linear_edge_im)

            elif self.seg_type == "kmeans":
                # clustering
                image = image / 255.0
                pic_n = image.reshape(image.shape[0] * image.shape[1], image.shape[2])
                kmeans = KMeans(n_clusters=5, random_state=0).fit(pic_n)
                pic2show = kmeans.cluster_centers_[kmeans.labels_]
                out_cur = pic2show.reshape(image.shape[0], image.shape[1], image.shape[2])

                linear_out_cur = out_cur.reshape(out_cur.shape[0] * out_cur.shape[1] * out_cur.shape[2])
                box_h = np.append(box_h, (ymax - ymin))
                box_w = np.append(box_w, (xmax - xmin))
                out_l = np.append(out_l, linear_out_cur)

        # region based
        """gray_r = gray.reshape(gray.shape[0] * gray.shape[1])
        for i in range(gray_r.shape[0]):
            print(i)
            if gray_r[i] > gray_r.mean():
                gray_r[i] = 1
            else:
                gray_r[i] = 0

        out_l = gray_r.reshape(gray.shape[0], gray.shape[1])"""

        return out_l, box_h, box_w

    def principal_axis(self, crop):
        X_row, X_col = np.where(crop > 200)

        X = np.zeros((len(X_row), 2))
        X[:, 0] = X_row
        X[:, 1] = X_col

        mean = np.empty((0))

        if len(X) > 0:
            _, eigenvectors, _ = cv2.PCACompute2(X, mean)
            principal_axis = eigenvectors[0, :]
        else:
            principal_axis = [0, 0]

        # PCA with sklearn
        """pca = PCA(n_components=1)
        if X.shape[0] > 0:
            pca.fit(X)
            principal_axis = pca.components_
        else:
            principal_axis = [[0,0]]"""

        return principal_axis

    def get_binary_crops(self, image, boxes_s):
        (h, w) = image.shape[:2]
        out_l = []
        box_h, box_w = [], []
        # crop image
        for i in range(boxes_s.shape[0]):
            xmin = (boxes_s[i, 0] * h).astype(int)
            ymin = (boxes_s[i, 1] * w).astype(int)
            xmax = (boxes_s[i, 2] * h).astype(int)
            ymax = (boxes_s[i, 3] * w).astype(int)
            crop = image[xmin:xmax, ymin:ymax]

            # Convert image to grayscale
            gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
            # cv2.imshow("GRAY", gray)
            # Convert image to binary

            if out_l == []:
                # out_l = ndimage.convolve(gray, self.kernel, mode='reflect')
                _, out_l = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
                out_l = out_l.reshape(out_l.shape[0] * out_l.shape[1])
                box_h = [(ymax - ymin)]
                box_w = [(xmax - xmin)]
            else:
                # edge_im = ndimage.convolve(gray, self.kernel, mode='reflect')
                _, bin_im = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
                linear_edge_im = bin_im.reshape(bin_im.shape[0] * bin_im.shape[1])
                box_h = np.append(box_h, (ymax - ymin))
                box_w = np.append(box_w, (xmax - xmin))
                out_l = np.append(out_l, linear_edge_im)

        return out_l, box_h, box_w

    def coordinates(self, track, camera):
        """Computes the real world 3D coordinates of a potato. The camera is considered to be the origine"""
        h, w = camera.h, camera.w

        [ymin, xmin, ymax, xmax] = track.box_sel
        dist = track.dist_sel

        x_mid = ((xmin + xmax) / 2).astype(int)
        y_mid = ((ymin + ymax) / 2).astype(int)

        if dist == []:
            return 0, 0, 0


        depth_frame = camera.frames.get_depth_frame()
        depth = np.asanyarray(depth_frame.get_data())

        profile = camera.pipeline.get_active_profile()
        depth_profile = rs.video_stream_profile(profile.get_stream(rs.stream.depth))
        depth_intrinsics = depth_profile.get_intrinsics()
        position = rs.rs2_deproject_pixel_to_point(depth_intrinsics, [x_mid, y_mid], dist)


        return position