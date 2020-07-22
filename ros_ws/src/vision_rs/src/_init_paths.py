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

from pathlib import Path


def add_path(path):
    if path not in sys.path:
        sys.path.insert(0, path)


currentPath = os.path.dirname(os.path.realpath(__file__))
workingPath = str(Path(currentPath).parents[3])

# Add lib to PYTHONPATH
visPath = os.path.join(workingPath, 'vision_lib')

add_path(workingPath)
add_path(visPath)
