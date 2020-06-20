#####################################################
##               Object detection from tensorflow trained model on Realsense Camera                ##
#####################################################
import os
import pyrealsense2 as rs
# Import Numpy for easy array manipulation
import numpy as np
# Import OpenCV for easy image rendering
import cv2
import tensorflow as tf

from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util
from imutils.video import FPS
from matplotlib.colors import hsv_to_rgb
from scipy import ndimage
from skimage.color import rgb2gray
from sklearn.cluster import KMeans




# Patch the location of gfile
tf.gfile = tf.io.gfile

INPUT_SOURCE = 'realsense'  #webcam or realsense
MODEL_NAME = 'mobilenet_v1_2'
# path to the frozen graph:
PATH_TO_FROZEN_GRAPH = 'trained_model/' + MODEL_NAME + '/frozen_inference_graph.pb'
# path to the label map
PATH_TO_LABEL_MAP = 'label_map.pbtxt'
# number of classes
NUM_CLASSES = 1


COLORS = np.random.uniform(0, 255, size=(NUM_CLASSES, 3))
THRESHOLD = 0.5
SEGMENTATION = "edge" #can be "edge", "kmeans"
#SKIP = 0
# defining the  filters
kernel_laplace = np.array([np.array([1, 1, 1]), np.array([1, -8, 1]), np.array([1, 1, 1])])
print(kernel_laplace, 'is a laplacian kernel')

def read_model():
    print("reads frozen graph")
    detection_graph = tf.Graph()
    with detection_graph.as_default():
        od_graph_def = tf.compat.v1.GraphDef()
        with tf.gfile.GFile(PATH_TO_FROZEN_GRAPH, 'rb') as fid:
            serialized_graph = fid.read()
            od_graph_def.ParseFromString(serialized_graph)
            tf.import_graph_def(od_graph_def, name='')

    print("reads label map")
    label_map = label_map_util.load_labelmap(PATH_TO_LABEL_MAP)
    categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES,
                                                                use_display_name=True)
    category_index = label_map_util.create_category_index(categories)

    return category_index, detection_graph


def object_detection(detection_graph, sess, image_np):
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

    boxes =   np.squeeze(boxes)
    classes = np.squeeze(classes)
    scores = np.squeeze(scores)

    return boxes, classes, scores

"""def remove_background(pipeline, align, clipping_distance):
            # Get frameset of color and depth
            frames = pipeline.wait_for_frames()
            # frames.get_depth_frame() is a 640x360 depth image

            # Align the depth frame to color frame
            aligned_frames = align.process(frames)

            # Get aligned frames
            aligned_depth_frame = aligned_frames.get_depth_frame()  # aligned_depth_frame is a 640x480 depth image
            color_frame = aligned_frames.get_color_frame()

            # Validate that both frames are valid
            if not aligned_depth_frame or not color_frame:
                return

            depth_image = np.asanyarray(aligned_depth_frame.get_data())
            color_image = np.asanyarray(color_frame.get_data())

            # Remove background - Set pixels further than clipping_distance to grey
            grey_color = 153
            depth_image_3d = np.dstack(
                (depth_image, depth_image, depth_image))  # depth image is 1 channel, color is 3 channels
            bg_removed = np.where((depth_image_3d > clipping_distance) | (depth_image_3d <= 0), grey_color, color_image)

            # Render images
            depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
            images = np.hstack((bg_removed, depth_colormap))
            cv2.namedWindow('Align Example', cv2.WINDOW_AUTOSIZE)
            cv2.imshow('Align Example', images)"""



"""def SSD_detect(image, frames, depth_scale):
    d=0
    (h, w) = image.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(image, (EXPECTED, EXPECTED)), 0.007843, (300, 300), 127.5)

    # pass the blob through the network and obtain the detections and
    # predictions
    #print("[INFO] computing object detections...")
    net.setInput(blob)
    detections = net.forward()

    # loop over the detections
    for i in np.arange(0, detections.shape[2]):
        # extract the confidence (i.e., probability) associated with the
        # prediction
        confidence = detections[0, 0, i, 2]

        # filter out weak detections by ensuring the `confidence` is
        # greater than the minimum confidence
        if confidence > argsv["confidence"]:
            # extract the index of the class label from the `detections`,
            # then compute the (x, y)-coordinates of the bounding box for
            # the object
            idx = int(detections[0, 0, i, 1])
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")

            d = compute_dist(frames, image, depth_scale, startX, startY, endX, endY)
            # display the prediction
            label = "{}: {:.2f}%".format(CLASSES[idx], confidence * 100)
            # print("[INFO] {}".format(label))
            cv2.rectangle(image, (startX, startY), (endX, endY),
                          COLORS[idx], 2)
            y = startY - 15 if startY - 15 > 15 else startY + 15
            cv2.putText(image, label, (startX, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2)


        else:
            startX, startY, endX, endY= [0,0,0,0]


    return startX, startY, endX, endY, image, d"""


def compute_dist(depth_frame, depth_scale, boxes):

    if len(boxes) == 0:
        dist = []
        return dist
    depth = np.asanyarray(depth_frame.get_data())
    (h, w) = depth.shape[:2]

    ymin = (boxes[:, 0]*h).astype(int)
    xmin = (boxes[:, 1]*w).astype(int)
    ymax = (boxes[:, 2]*h).astype(int)
    xmax = (boxes[:, 3]*w).astype(int)
    #stream alignment




    #xmin_depth = int((xmin * EXPECTED) * depth_scale)
    #ymin_depth = int((ymin * EXPECTED) * depth_scale)
    #xmax_depth = int((xmax * EXPECTED) * depth_scale)
    #ymax_depth = int((ymax * EXPECTED) * depth_scale)
    #print(xmin_depth)
    #print(xmax_depth)

    dist = np.zeros(len(xmin))
    # Crop depth data:
    for i in range(len(xmin)):
        depth = depth[xmin[i]:xmax[i], ymin[i]:ymax[i]].astype(float)

        # Get data scale from the device and
        depth = depth * depth_scale
        print(depth_scale)
        print(depth)

        #dist[i], _, _, _ = cv2.minMaxLoc(depth)
        dist[i], _, _, _ = cv2.mean(depth)


    return dist

"""def run_SSD():
    try:

        # Create pipeline
        pipeline = rs.pipeline()

        # Create a config object
        config = rs.config()

        # Configure the pipeline to stream the depth stream
        config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
        config.enable_stream(rs.stream.color, 640, 480, rs.format.rgb8, 30)
        # Start streaming from file
        profile = pipeline.start(config)

        #depth_scale = profile.get_device().first_depth_sensor().get_depth_scale()

        colorizer = rs.colorizer()
        # Getting the depth sensor's depth scale (see rs-align example for explanation)
        depth_sensor = profile.get_device().first_depth_sensor()
        depth_scale = depth_sensor.get_depth_scale()
        print("Depth Scale is: ", depth_scale)

        # We will be removing the background of objects more than
        #  clipping_distance_in_meters meters away
        clipping_distance_in_meters = 1
        clipping_distance = clipping_distance_in_meters / depth_scale

        # Create an align object
        # rs.align allows us to perform alignment of depth frames to others frames
        # The "align_to" is the stream type to which we plan to align depth frames.
        align_to = rs.stream.color
        align = rs.align(align_to)

        # Create opencv window to render image in
        #cv2.namedWindow("Depth Stream", cv2.WINDOW_AUTOSIZE)

        # Streaming loop
        while True:
            # Get frameset of depth
            frames = pipeline.wait_for_frames()

            # Get depth frame
            depth_frame = frames.get_depth_frame()
            rgb_frame = frames.get_color_frame()


            # Colorize depth frame to jet colormap
            depth_color_frame = colorizer.colorize(depth_frame)

            # Convert depth_frame to numpy array to render image in opencv
            depth_color_image = np.asanyarray(depth_color_frame.get_data())
            rgb_image = np.asanyarray(rgb_frame.get_data())
            rgb_image = cv2.cvtColor(rgb_image, cv2.COLOR_BGR2RGB)

            startX, startY, endX, endY, image, d = SSD_detect(rgb_image, frames, depth_scale)

            clipping_distance_in_meters = d
            print(d)
            clipping_distance = clipping_distance_in_meters / depth_scale
            remove_background(pipeline, align, clipping_distance)


            # show the output image
            cv2.imshow("Output", image)


            # Render image in opencv window
            #cv2.imshow("Depth Stream", depth_color_image)



            key = cv2.waitKey(1)
            # if pressed escape exit program
            if key == 27:
                cv2.destroyAllWindows()
                break

    finally:
        pass"""


def start_RS():
    # Create pipeline
    pipeline = rs.pipeline()
    # Create a config object
    config = rs.config()
    # Configure the pipeline to stream the depth stream
    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
    config.enable_stream(rs.stream.color, 640, 480, rs.format.rgb8, 30)
    # Start streaming from file
    profile = pipeline.start(config)
    depth_sensor = profile.get_device().first_depth_sensor()
    depth_scale = depth_sensor.get_depth_scale()

    colorizer = rs.colorizer()
    # Getting the depth sensor's depth scale (see rs-align example for explanation)
    #depth_sensor = profile.get_device().first_depth_sensor()
    #depth_scale = depth_sensor.get_depth_scale()
    #print("Depth Scale is: ", depth_scale)

    # We will be removing the background of objects more than
    #  clipping_distance_in_meters meters away
    #clipping_distance_in_meters = 1
    #clipping_distance = clipping_distance_in_meters / depth_scale

    # Create an align object
    # rs.align allows us to perform alignment of depth frames to others frames
    # The "align_to" is the stream type to which we plan to align depth frames.
    #align_to = rs.stream.color
    #align = rs.align(align_to)

    # Create opencv window to render image in
    # cv2.namedWindow("Depth Stream", cv2.WINDOW_AUTOSIZE)
    return pipeline, colorizer, depth_scale


def get_frames_from_RS(pipeline, colorizer):
    # Get frameset of depth
    frames = pipeline.wait_for_frames()
    # Create alignment primitive with color as its target stream:
    align = rs.align(rs.stream.color)
    frames = align.process(frames)
    # Update color and depth frames:
    depth_frame = frames.get_depth_frame()
    colorized_depth = np.asanyarray(colorizer.colorize(depth_frame).get_data())
    # Get depth frame
    rgb_frame = frames.get_color_frame()

    # Colorize depth frame to jet colormap
    colorized_depth = colorizer.colorize(depth_frame)
    # Convert depth_frame to numpy array to render image in opencv
    colorized_depth = np.asanyarray(colorized_depth.get_data())
    rgb_image = np.asanyarray(rgb_frame.get_data())
    rgb_image = cv2.cvtColor(rgb_image, cv2.COLOR_BGR2RGB)

    return rgb_image, colorized_depth, frames

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
           cv2.putText(image_np, "dist: " + str(round(dist[i], 2)) + " [m]", coor, cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 255))

    cv2.imshow(name, image_np) #cv2.resize(image_np, (1200, 800)


def select_objects(boxes, classes, scores, thres):
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





def instance_seg(image, boxes_s):
    (h, w) = image.shape[:2]
    out_l = []
    box_h, box_w = [], []
    #crop image
    for i in range(boxes_s.shape[0]):
        xmin = (boxes_s[i, 0] * h).astype(int)
        ymin = (boxes_s[i, 1] * w).astype(int)
        xmax = (boxes_s[i, 2] * h).astype(int)
        ymax = (boxes_s[i, 3] * w).astype(int)
        crop = image[xmin:xmax, ymin:ymax]


        #edge detection
        if SEGMENTATION == "edge":
            # converting to grayscale
            gray = rgb2gray(crop)
            if out_l == []:
                out_l = ndimage.convolve(gray, kernel_laplace, mode='reflect')
                out_l = out_l.reshape(out_l.shape[0]*out_l.shape[1])
                box_h = [(ymax-ymin)]
                box_w = [(xmax-xmin)]
            else:
                edge_im = ndimage.convolve(gray, kernel_laplace, mode='reflect')
                linear_edge_im = edge_im.reshape(edge_im.shape[0]*edge_im.shape[1])
                box_h = np.append(box_h, (ymax-ymin))
                box_w = np.append(box_w, (xmax-xmin))
                print("shape pre", np.shape(out_l))
                print("shape lin", np.shape(edge_im))
                out_l = np.append(out_l, linear_edge_im)
                print("shape", np.shape(out_l))

        elif SEGMENTATION == "kmeans":
            # clustering
            image = image/255.0
            pic_n = image.reshape(image.shape[0] * image.shape[1], image.shape[2])
            kmeans = KMeans(n_clusters=5, random_state=0).fit(pic_n)
            pic2show = kmeans.cluster_centers_[kmeans.labels_]
            out_l = pic2show.reshape(image.shape[0], image.shape[1], image.shape[2])

    #region based
    """gray_r = gray.reshape(gray.shape[0] * gray.shape[1])
    for i in range(gray_r.shape[0]):
        print(i)
        if gray_r[i] > gray_r.mean():
            gray_r[i] = 1
        else:
            gray_r[i] = 0

    out_l = gray_r.reshape(gray.shape[0], gray.shape[1])"""


    return out_l, box_h, box_w
    #plt.imshow(out_l, cmap='gray')

def process_image():
    #i = float('Inf')

    category_index, detection_graph = read_model()

    pipeline, colorizer, depth_scale = start_RS()

    with detection_graph.as_default():
        with tf.compat.v1.Session(graph=detection_graph) as sess:
            while True:

                image_np, colorized_depth, frames = get_frames_from_RS(pipeline, colorizer)

                #i = i+1
                #if i > SKIP:
                #i = 0

                boxes, classes, scores = object_detection(detection_graph, sess, image_np)
                boxes_s, classes_s, scores_s = select_objects(boxes, classes, scores, THRESHOLD)
                dist = compute_dist(frames.get_depth_frame(), depth_scale, boxes_s)

                mask_im, box_h, box_w = instance_seg(colorized_depth, boxes_s)
                display_output(image_np, boxes_s, classes_s, scores_s, category_index, dist, 'RGB')
                display_output(colorized_depth, boxes_s, classes_s, scores_s, category_index, dist, 'Depth')
                #display_output(mask_im, boxes_s, classes_s, scores_s, category_index, dist, 'Mask')
                if mask_im != []:
                    buff = 0
                    for i in range(boxes_s.shape[0]):
                        nb_pixels = box_h[i]*box_w[i]
                        mask_im_cur = mask_im[buff:(buff+nb_pixels)]
                        mask_im_cur = np.reshape(mask_im_cur, (box_w[i], box_h[i]))
                        cv2.imshow("mask " + str(i), mask_im_cur)
                        buff = buff + nb_pixels

                """print("a")

                print(np.shape(classes))
                print(np.shape(scores))
                print(np.shape(boxes))"""



                if cv2.waitKey(25) & 0xFF == ord('q'):
                    cv2.destroyAllWindows()
                    break

if __name__ == '__main__':
    #run_SSD()


    process_image()
