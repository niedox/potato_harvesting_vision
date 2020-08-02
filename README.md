# potato_harvesting_vision
Computer vision algorithm for harvesting of potatoes growing in aeroponics with a robotic arm.
Potato Detection and Pose Estimation (3D-coordinates, size, orientation) are performed.
Camera: Intel Realsense D415


# Repository structure

- main.py runs the computer vision algorithm

- "ros_ws" is the ROS workspace. The script main_ros.py runs the algorithm and publishes the computed variables in a ROS topic

- "evaluation" contains the scripts and data used to assess the algorithm performances

- "training" contains the jupyter notebook and configuration files used to train the object detection networks

- "vision lib" contains the code used to detect the potatoes, compute their pose and displayy the results

