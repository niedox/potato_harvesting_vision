import numpy as np
import cv2
import tensorflow as tf

from object_detection.utils import label_map_util
from scipy import ndimage
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA


# Patch the location of gfile
tf.gfile = tf.io.gfile



class ImageProcessing():

    def __init__(self, path_to_frozen_graph, path_to_label_map, num_classes, seg_type):

        #object detection NN parameter
        self.path_to_frozen_graph = path_to_frozen_graph
        self.path_to_label_map = path_to_label_map
        self.num_classes = num_classes

        #segmentation parameters
        self.seg_type = seg_type
        self.kernel = np.array([np.array([1, 1, 1]), np.array([1, -8, 1]), np.array([1, 1, 1])])

        #get model
        self.read_model()

    def read_model(self):
        print("reads frozen graph")
        detection_graph = tf.Graph()
        with detection_graph.as_default():
            od_graph_def = tf.compat.v1.GraphDef()
            with tf.gfile.GFile(self.path_to_frozen_graph, 'rb') as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name='')

        print("reads label map")
        label_map = label_map_util.load_labelmap(self.path_to_label_map)
        categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=self.num_classes,
                                                                    use_display_name=True)
        category_index = label_map_util.create_category_index(categories)

        return category_index, detection_graph

    def object_detection(self, detection_graph, sess, image_np):
        # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
        image_np_expanded = np.expand_dims(image_np, axis=0)
        # Extract image tensor
        image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
        # Extract detection boxes
        boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
        # Extract detection scores
        scores = detection_graph.get_tensor_by_name('detection_scores:0')
        # Extract detection classes
        classes = detection_graph.get_tensor_by_name('detection_classes:0')
        # Extract number of detections
        num_detections = detection_graph.get_tensor_by_name(
            'num_detections:0')
        # Actual detection.
        (boxes, scores, classes, num_detections) = sess.run(
            [boxes, scores, classes, num_detections],
            feed_dict={image_tensor: image_np_expanded})

        boxes = np.squeeze(boxes)
        classes = np.squeeze(classes)
        scores = np.squeeze(scores)

        return boxes, classes, scores

    def select_objects(self, boxes, classes, scores, thres):
        idx = np.where(scores >= thres)[0]
        if idx.size > 0:
            boxes = boxes[idx, :]
            classes = classes[idx]
            scores = scores[idx]

        else:
            boxes = []
            classes = []
            scores = []

        return np.array(boxes), np.array(classes), np.array(scores)


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
            if xmax < w-margin:
                xmax = xmax + margin
            ymax = (boxes_s[i, 3] * w + margin).astype(int)
            if ymax < h-margin:
                ymax = ymax + margin
            crop = image[xmin:xmax, ymin:ymax]

            # edge detection
            if self.seg_type == "edge":
                print(self.kernel, 'is a laplacian kernel')
                # converting to grayscale
                #gray = rgb2gray(crop)
                gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
                gray = cv2.bilateralFilter(gray, 11, 17, 17)
                #cv2.imshow("GRAY", gray)

                if out_l == []:
                    #out_l = ndimage.convolve(gray, self.kernel, mode='reflect')
                    out_l = cv2.Canny(gray, 30, 200)
                    out_l = out_l.reshape(out_l.shape[0] * out_l.shape[1])
                    box_h = [(ymax - ymin)]
                    box_w = [(xmax - xmin)]
                else:
                    #edge_im = ndimage.convolve(gray, self.kernel, mode='reflect')
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
            principal_axis = [0,0]

        #PCA with sklearn
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
            #cv2.imshow("GRAY", gray)
            # Convert image to binary


            if out_l == []:
                # out_l = ndimage.convolve(gray, self.kernel, mode='reflect')
                _ , out_l = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
                out_l = out_l.reshape(out_l.shape[0] * out_l.shape[1])
                box_h = [(ymax - ymin)]
                box_w = [(xmax - xmin)]
            else:
                # edge_im = ndimage.convolve(gray, self.kernel, mode='reflect')
                _ , bin_im = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
                linear_edge_im = bin_im.reshape(bin_im.shape[0] * bin_im.shape[1])
                box_h = np.append(box_h, (ymax - ymin))
                box_w = np.append(box_w, (xmax - xmin))
                out_l = np.append(out_l, linear_edge_im)

        return out_l, box_h, box_w

