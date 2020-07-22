#################################h##########################################################
#                                                                                         #
# Set up paths for the Object Detection Metrics                                           #
#                                                                                         #
# Developed by: Rafael Padilla (rafael.padilla@smt.ufrj.br)                               #
#        SMT - Signal Multimedia and Telecommunications Lab                               #
#        COPPE - Universidade Federal do Rio de Janeiro                                   #
#        Last modification: May 24th 2018                                                 #
###########################################################################################

import sys
import os


def add_path(path):
    if path not in sys.path:
        sys.path.insert(0, path)


currentPath = os.path.dirname(os.path.realpath(__file__))

# Add lib to PYTHONPATH
libPath = os.path.join(currentPath, 'evaluation/lib')
visPath = os.path.join(currentPath, 'ros_ws/src/vision_rs/src/vision_lib')

add_path(currentPath)
add_path(visPath)
add_path(libPath)
