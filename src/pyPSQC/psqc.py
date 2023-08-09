import time

from pyPSQC.prepare_data import prepare_data
from pyPSQC.feature_extraction import feature_extraction
from pyPSQC.quality_prediction import quality_prediction

"""
This is the python version of the:
"A quality control system for automated prostate segmentation on T2-weighted MRI".

This is a fully automated quality control system that generate a quality score and class 
for assessing the accuracy of automated prostate segmentations on T2W MR imagese.
This fully automated quality control system employs radiomics features for estimating the quality
of deep-learning based prostate segmentation on T2W MR images.
The performance of our system is developed and tested using two data cohorts and 4 different deep-learning based segmentation algorithms

The method was developed at the CIMORe group at the Norwegian University of Science and Technology (NTNU) in Trondheim, Norway. https://www.ntnu.edu/isb/cimore
For detailed information about this method, please read our paper: https://www.mdpi.com/2075-4418/10/9/714-020-00871-3

AUTHOR = 'Mohammed R. S. Sunoqrot'
AUTHOR_EMAIL = 'mohammed.sunoqrot@ntnu.no'
LICENSE = 'MIT'
GitHub: https://github.com/MohammedSunoqrot/pyPSQC
"""


def psqc(input_image_path, input_mask_path, input_normalized=False, quality_class_threshold=85):
    """
    Measure the quality of automated prostate segmentation.

    Parameters:
        input_image_path (str): The file path to the input 3D image (any supported SimpleITK format) or to the DICOM folder.
        input_mask_path (str): Path to the corresponding mask of the input 3D image. Any supported SimpleITK format or DICOM folder.
        input_normalized (bool, optional): Whether the input image is normalized. Default is False.
        quality_class_threshold (float, optional): Threshold for classifying quality. It can be between [0 - 100]. Default is 85.

    Returns:
        quality_score (float): Calculated and capped quality score. It represents a perecentage [min = 0%, max 100%].
        quality_class (str): Classification result ("Acceptable" or "NOT Acceptable").
    """
    # Measure the time taken for processing
    start_time = time.time()

    # Print that the method started processing
    print(
        f"=> Started measuring the quality of automated prostate segmentation of: image {input_image_path} and mask {input_mask_path}")

    # Prepare input image and mask
    image, mask = prepare_data(input_image_path, input_mask_path,
                               input_normalized)

    # Feature extraction to serve as predictors to the LASSO model
    features_values = feature_extraction(image, mask)

    # Quality prediction using a trained LASSO model
    quality_score, quality_class = quality_prediction(
        features_values, quality_class_threshold)

    # Print quality score and quality class
    print(
        f"--> Quality Score = {quality_score}%, Quality Class: {quality_class}")

    # Measure the time taken for processing
    end_time = time.time()
    processing_time = end_time - start_time
    print("==> Done with measuring the quality of automated prostate segmentation. Time taken: {:.2f} seconds".format(
        processing_time))

    # Return the mask quality score and class
    return quality_score, quality_class
