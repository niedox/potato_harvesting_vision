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
        x = (xmax[i] - xmin[i])/2 + xmin[i]
        y = (ymax[i] - ymin[i])/2 + ymin[i]
        """depth = depth[xmin[i]:xmax[i], ymin[i]:ymax[i]].astype(float)
        # Get data scale from the device and
        depth = depth * depth_scale

        #dist[i], _, _, _ = cv2.minMaxLoc(depth)
        dist[i], _, _, _ = cv2.mean(depth)"""
        dist[i] = depth_frame.get_distance(int(x), int(y))

    return dist

def get_coor(x, y, depth, pipeline):
    profile = pipeline.get_active_profile()
    depth_profile = rs.video_stream_profile(profile.get_stream(rs.stream.depth))
    depth_intrinsics = depth_profile.get_intrinsics()

    result = rs.rs2_deproject_pixel_to_point(depth_intrinsics, [x, y], depth)
    return result[0], result[1], result[2]

def compute_angle(axis):
    y = axis[0]
    x = axis[1]

    if x == 0:
        return 0
    else:
        angle = np.arctan(y/x)
    return angle


#def get_pixel_dist:

def compute_size(box, dist, h, w, pipeline):

    #coor in pixels
    ymin = (box[0] * h).astype(int)
    xmin = (box[1] * w).astype(int)
    ymax = (box[2] * h).astype(int)
    xmax = (box[3] * w).astype(int)

    xmid = (xmin+xmax)/2
    ymid = (ymin+ymax)/2

    xmid_m, ymid_m, _ = get_coor(xmid, ymid, dist, pipeline)

    xmid_wrt_center = xmid -w/2
    ymid_wrt_center = ymid -h/2

    ratio_x = xmid_wrt_center/xmid_m
    ratio_y = ymid_wrt_center/ymid_m

    box_height = (ymax-ymin)/ratio_y
    box_width = (xmax-xmin)/ratio_x

    return box_height, box_width




