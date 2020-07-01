import RS_camera
import cv2

pipeline, colorizer, depth_scale = RS_camera.start_RS()
photo_idx = 106
while True:

    image_np, colorized_depth, frames = RS_camera.get_frames(pipeline, colorizer)
    cv2.imshow("RGB", image_np)

    if cv2.waitKey(25) & 0xFF == ord('p'):
        cv2.imwrite('RS_photos/image' + str(photo_idx) + '.png', image_np)
        photo_idx = photo_idx + 1
        print("photo" + str(photo_idx))

