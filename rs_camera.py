import pyrealsense2 as rs
import cv2
import numpy as np

class RS_camera():

    def __init__(self):

        self.pipeline = None
        self.colorizer = None
        self.depth_scale = None
        self.start_RS()

        self.frames = None
        self.rgb_image = None
        self.colorized_depth = None
        self.h = 0
        self.w = 0


    def start_RS(self):
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

        self.pipeline = pipeline
        self.depth_scale = depth_sensor.get_depth_scale()
        self.colorizer = rs.colorizer()

    def get_frames(self):
        # Get frameset of depth
        frames = self.pipeline.wait_for_frames()
        # Create alignment primitive with color as its target stream:
        align = rs.align(rs.stream.color)
        frames = align.process(frames)
        # Update color and depth frames:
        depth_frame = frames.get_depth_frame()
        colorized_depth = np.asanyarray(self.colorizer.colorize(depth_frame).get_data())
        # Get depth frame
        rgb_frame = frames.get_color_frame()

        # Colorize depth frame to jet colormap
        colorized_depth = self.colorizer.colorize(depth_frame)
        # Convert depth_frame to numpy array to render image in opencv
        colorized_depth = np.asanyarray(colorized_depth.get_data())
        rgb_image = np.asanyarray(rgb_frame.get_data())
        rgb_image = cv2.cvtColor(rgb_image, cv2.COLOR_BGR2RGB)

        self.rgb_image = rgb_image
        self.colorized_depth = colorized_depth
        self.frames = frames
        self.h, self.w = rgb_image.shape[:2]



