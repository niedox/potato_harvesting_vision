import numpy as np
import cv2

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

#def get_pixel_dist:


"""def get_coor(image, depth_frame, boxes):
    (h,w) = image.shape[:2]
    center = [int(h/2), int(w/2)]"""



