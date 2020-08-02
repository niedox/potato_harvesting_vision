# Folder to evaluate the algorithm performances

## mAP computations
- The test set's .xml label files should be stored in "igluna_xml"
- Run convert.py to convert the .xml files in the suited .txt format
- Run store_detections.py to get the object detections of a model (model path to be specified in the script)
- Run compute_map.py to calculate the mean Average Precision. 

compute_map.py is a copy of pascalvoc.py from https://github.com/rafaelpadilla/Object-Detection-Metrics and requieres arguments. For the script's arguments, please refer to the original GitHub page.

## Orientation test

- The images to test the orientaion estimation performances are meant to be stored in "orientation test"
- photo.py can be used to make pictures with RS camera D415.
- Run test_orientation.py to calculate the precsion and accuracy of the orientation estimation.  The orientation estimation methods can be chosen at the beginning of the script.
