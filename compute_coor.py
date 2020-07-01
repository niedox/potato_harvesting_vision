import numpy as np
import cv2
import pyrealsense2 as rs

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

        #dist[i], _, _, _ = cv2.minMaxLoc(depth)
        dist[i], _, _, _ = cv2.mean(depth)

    return dist

def get_coor(x, y, depth, pipeline):
    profile = pipeline.get_active_profile()
    depth_profile = rs.video_stream_profile(profile.get_stream(rs.stream.depth))
    depth_intrinsics = depth_profile.get_intrinsics()

    result = rs.rs2_deproject_pixel_to_point(depth_intrinsics, [x, y], depth)
    #result[0]: right, result[1]: down, result[2]: forward
    return result[2], -result[0], -result[1]

#def get_pixel_dist:


"""def get_coor(image, depth_frame, boxes):
    (h,w) = image.shape[:2]
    center = [int(h/2), int(w/2)]"""



