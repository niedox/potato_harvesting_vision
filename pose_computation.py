import numpy as np

class Pose():
    def __init__(self, seg_type):

        # segmentation parameters
        self.seg_type = seg_type
        self.kernel = np.array([np.array([1, 1, 1]), np.array([1, -8, 1]), np.array([1, 1, 1])])

        #box dimensions (in meters)
        self.box_h = 0
        self.box_w = 0

        #potato position
        self.position = [0, 0] #x,y (in meters)
        self.angle    = 0      #in radian


    def instance_seg(self, image, boxes_s):
        (h, w) = image.shape[:2]
        out_l = []
        box_h, box_w = [], []
        margin = 0
        # crop image
        for i in range(boxes_s.shape[0]):
            xmin = (boxes_s[i, 0] * h).astype(int)
            if xmin > margin:
                xmin = xmin - margin
            ymin = (boxes_s[i, 1] * w - margin).astype(int)
            if ymin > margin:
                ymin = ymin - margin
            xmax = (boxes_s[i, 2] * h + margin).astype(int)
            if xmax < w - margin:
                xmax = xmax + margin
            ymax = (boxes_s[i, 3] * w + margin).astype(int)
            if ymax < h - margin:
                ymax = ymax + margin
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
        # plt.imshow(out_l, cmap='gray')

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