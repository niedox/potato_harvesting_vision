"""Script to make photos with the Camera RealSense D415"""


import cv2
import os
import numpy as np

from vision_lib.rs_camera import RS_camera


camera = RS_camera()
photo_idx = 0

while True:

    camera.get_frames()
    image_rgb = camera.rgb_image.copy()
    colorized_depth = camera.colorized_depth.copy()


    cv2.imshow("Perception", np.hstack((cv2.cvtColor(image_rgb, cv2.COLOR_BGR2RGB), colorized_depth)))

    #press "p" to make a photo
    if cv2.waitKey(25) & 0xFF == ord('p'):

        #store photo
        cv2.imwrite('orientation_test/image' + str(photo_idx) + '.png', cv2.cvtColor(image_rgb, cv2.COLOR_BGR2RGB))
        cv2.imwrite('orientation_test/image' + str(photo_idx+1) + '.png', colorized_depth)

        print("photo #" + str(photo_idx))
        photo_idx = photo_idx + 2


