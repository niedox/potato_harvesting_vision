The .ipynb file is used to train the object detection models on Google Colab (with Tensorflow). 
To train a model on own custom data, a folder called training_demo with the following structure is required:

    └── training_demo
        ├── annotations
        ├── config_files
        ├── images
        │   ├── test
        │   └── train
        ├── preprocessing
        ├── pre-trained-models
        ├── saved_trained_models
        └── training

Note that:
- "config_files" must contain the configuration file used for training. The configurations used for this project are provided. More .config files can be found on the Tensorflow GitHub.
- "images" must contain the training images and .xml label files. The data-set will then be divided into a training set and test set. 
- "preprocessing" is provided and contains scripts that set the data in the right format for training
- "pre-trained-models" is meant to contain pre-trained-models obtained from the tensorflow detection zoo.

For more details about how the models are trained, see the following tutorial: https://medium.com/analytics-vidhya/training-an-object-detection-model-with-tensorflow-api-using-google-colab-4f9a688d5e8b 




