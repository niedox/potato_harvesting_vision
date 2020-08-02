# potato_harvesting_vision
Computer vision algorithm for harvesting of potatoes growing in aeroponics with a robotic arm.
Potato Detection and Pose Estimation (3D-coordinates, size, orientation) are performed.
Camera: Intel Realsense D415


## Repository structure

- main.py runs the computer vision algorithm

- "ros_ws" is the ROS workspace. The script main_ros.py runs the algorithm and publishes the computed variables in a ROS topic

- "evaluation" contains the scripts and data used to assess the algorithm performances

- "training" contains the jupyter notebook and configuration files used to train the object detection networks

- "vision lib" contains the code used to detect the potatoes, compute their pose and displayy the results

## Parameters

At the beginning of main.py and main_ros.py, the following algorithm parameters can be set:
- MODEL_NAME: name of the object detection model
- THRESHOLD: Score threshold above which the detected object are considered.
- SEG_TYPE: Image segmentation technique used for the orientation estimation (Canny Edge Detectio or K-Means)
- POSE_TYPE: Orientation estimation technique (PCA or Ellipse Fitting)        
- RIPENESS_THRES: Area above which potato are considered as ripe (in squared meters)
- EPSILON: proximity threshold for tracking
- TRACKING_LIM: nb of consecutive tracking frames at which tracking is reinitialized .
- DISPLAY: Boolean to activate/deactivate display

