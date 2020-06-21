import pyrealsense2 as rs
import cv2
import numpy as np

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

def get_frames(pipeline, colorizer):
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

def get_dist(depth_frame, depth_scale, boxes):

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
