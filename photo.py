import RS_camera
import cv2

pipeline, colorizer, depth_scale = RS_camera.start_RS()
photo_idx = 0
while True:

    image_np, colorized_depth, frames = RS_camera.get_frames(pipeline, colorizer)
    cv2.imshow("RGB", image_np)

    if cv2.waitKey(25) & 0xFF == ord('p'):
        cv2.imwrite('RS_photos/image' + str(photo_idx) + '.png', image_np)

    if cv2.waitKey(25) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        break
