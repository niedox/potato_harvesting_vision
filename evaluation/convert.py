import os
import xml.etree.ElementTree as ET
import numpy as np


XML_DIR = "evaluation/igluna_xml/"
GROUNDTRUTH_DIR = "evaluation/groundtruth/"

def read_content(xml_file: str):

    tree = ET.parse(xml_file)
    root = tree.getroot()
    list_with_all_boxes = []
    class_list = []

    for object in root.iter('object'):

        filename = root.find('filename').text

        ymin, xmin, ymax, xmax = None, None, None, None

        for box in object.findall("bndbox"):
            ymin = int(box.find("ymin").text)
            xmin = int(box.find("xmin").text)
            ymax = int(box.find("ymax").text)
            xmax = int(box.find("xmax").text)

        object_class = object.find("name").text

        class_list.append(object_class)
        list_with_single_boxes = [xmin, ymin, xmax, ymax]
        list_with_all_boxes.append(list_with_single_boxes)

    return list_with_all_boxes, class_list

i = 0
for filename in os.listdir(XML_DIR):
    boxes, class_list = read_content(XML_DIR + filename)

    f = open(GROUNDTRUTH_DIR + "file" + str(i) + ".txt", "x")
    i = i + 1

    for j in range(len(class_list)):
        f.write(str(class_list[j]))
        for k in range(4):
            print(j, k)
            f.write(" " + str(boxes[j][k]))
        f.write("\n")