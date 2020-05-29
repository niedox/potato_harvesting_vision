#####################################################
##               Object detection from tensorflow trained model on Realsense Camera                ##
#####################################################

import pyrealsense2 as rs
# Import Numpy for easy array manipulation
import numpy as np
# Import OpenCV for easy image rendering
import cv2
import tensorflow as tf

from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util
from imutils.video import FPS


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


#COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))
#EXPECTED = 400


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

"""def compute_dist(frames, image, depth_scale, xmin, ymin, xmax, ymax):

    (h, w) = image.shape[:2]

    #stream alignment
    # Create alignment primitive with color as its target stream:
    align = rs.align(rs.stream.color)
    frames = align.process(frames)

    # Update color and depth frames:
    aligned_depth_frame = frames.get_depth_frame()
    #colorized_depth = np.asanyarray(colorizer.colorize(aligned_depth_frame).get_data())

    scale = float(h)/float(EXPECTED)

    #xmin_depth = int((xmin * EXPECTED) * scale)
    #ymin_depth = int((ymin * EXPECTED) * scale)
    #xmax_depth = int((xmax * EXPECTED) * scale)
    #ymax_depth = int((ymax * EXPECTED) * scale)
    #print(xmin_depth)
    #print(xmax_depth)
    depth = np.asanyarray(aligned_depth_frame.get_data())
    # Crop depth data:
    depth = depth[xmin:xmax, ymin:ymax].astype(float)

    # Get data scale from the device and convert to meters

    depth = depth * depth_scale
    dist, _, _, _ = cv2.mean(depth)

    return dist"""

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

    # depth_scale = profile.get_device().first_depth_sensor().get_depth_scale()

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
    return pipeline, colorizer

def get_frames_from_RS(pipeline, colorizer):
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

    return rgb_image

def display_output(image_np, boxes, classes, scores, category_index):
    # Visualization of the results of a detection.
    vis_util.visualize_boxes_and_labels_on_image_array(
        image_np,
        np.squeeze(boxes),
        np.squeeze(classes).astype(np.int32),
        np.squeeze(scores),
        category_index,
        use_normalized_coordinates=True,
        line_thickness=3,
    )
    cv2.imshow('Detection', cv2.resize(image_np, (1200, 800)))



def process_image():
    category_index, detection_graph = read_model()

    pipeline, colorizer = start_RS()

    with detection_graph.as_default():
        with tf.compat.v1.Session(graph=detection_graph) as sess:
            while True:
                image_np = get_frames_from_RS(pipeline, colorizer)

                boxes, classes, scores = object_detection(detection_graph, sess, image_np)
                print("a")

                print(len(classes[0]))
                print(len(scores[0]))
                print(boxes)

                display_output(image_np, boxes, classes, scores, category_index)

                if cv2.waitKey(25) & 0xFF == ord('q'):
                    cv2.destroyAllWindows()
                    break

if __name__ == '__main__':
    #run_SSD()
    process_image()
