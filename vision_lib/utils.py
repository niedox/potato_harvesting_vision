import numpy as np
import cv2



def compute_center(box):
    ymid = ((box[0] + box[2])/2).astype(int)
    xmid = ((box[1] + box[3])/2).astype(int)

    return [xmid, ymid]




