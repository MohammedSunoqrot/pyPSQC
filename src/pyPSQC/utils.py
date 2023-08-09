import radiomics
import SimpleITK as sitk
import numpy as np
import math
import json
import os


def read_sitk_image(file_path):
    """
    Reads an image file (with supported SimpleITK format) and returns a SimpleITK image object.

    Parameters:
        file_path (str): The path to the file/folder(for DICOM).

    Returns:
        image (SimpleITK.Image): The SimpleITK image object representing the image.
    """

    # Check if the input path corresponds to a DICOM directory.
    # Check if the output_file_path has no file extension
    if not os.path.splitext(file_path)[1]:
        reader = sitk.ImageSeriesReader()
        series_ids = reader.GetGDCMSeriesIDs(file_path)

        if len(series_ids) > 0:
            # It is DICOM directory
            # Get the DICOM files and then read them as a 3D image
            dicom_names = reader.GetGDCMSeriesFileNames(file_path)
            reader.SetFileNames(dicom_names)
            image = reader.Execute()
        else:
            # It is not DICOM directory
            # Read the image
            image = sitk.ReadImage(file_path)
    else:
        # It is not DICOM directory
        # Read the image
        image = sitk.ReadImage(file_path)

    return image


def get_settings(image_array_in, mask_array_in, nr_bins):
    """
    Calculate settings for radiomics feature extraction.

    Parameters:
        image_array_in (numpy.ndarray): Input image array.
        mask_array_in (numpy.ndarray): Input mask array.
        nr_bins (int): Number of bins for intensity histogram.

    Returns:
        settings (dict): Radiomics extraction settings.
    """
    # Calculate intensity range for quantization
    mask_sum = np.sum(mask_array_in)

    if mask_sum == 0:
        raise ValueError("Mask is empty. Cannot compute intensity range.")

    intensity_range = np.max(
        image_array_in[mask_array_in != 0]) - np.min(image_array_in[mask_array_in != 0])

    # Define radiomics settings
    settings = {}
    settings['binWidth'] = intensity_range / nr_bins
    settings['correctMask'] = True

    return settings


def get_slice_from_mask(mask_in, slice_nr_in):
    """
    Extract a slice from a mask.

    Parameters:
        mask_in (SimpleITK.Image): Input mask image.
        slice_nr_in (int): Index of the slice to extract.

    Returns:
        new_mask (SimpleITK.Image): Extracted slice mask.
    """
    # Convert mask to NumPy array
    mask_array = sitk.GetArrayFromImage(mask_in)

    # Create a new mask array with zeros
    new_mask_array = np.zeros_like(mask_array)
    new_mask_array[:, :, :] = 0

    # Copy the specified slice from the original mask
    new_mask_array[slice_nr_in, :, :] = mask_array[slice_nr_in, :, :]

    # Create a new SimpleITK mask image from the NumPy array
    new_mask = sitk.GetImageFromArray(new_mask_array)

    # Copy metadata from the original mask
    new_mask.CopyInformation(mask_in)

    return new_mask


def extract_features(image, mask, feature_class):
    """
    Extract radiomics features for a given image and mask.

    Parameters:
        image (SimpleITK.Image): Input image.
        mask (SimpleITK.Image): Input mask.
        feature_class (str): Feature class name.

    Returns:
        dict: Extracted radiomics feature vector.
    """
    # Get image and mask arrays
    image_array = sitk.GetArrayFromImage(image)
    mask_array = sitk.GetArrayFromImage(mask)

    # Get radiomics settings
    settings = get_settings(image_array, mask_array, 64)

    # Create a radiomics feature extractor with the specified settings
    extractor = radiomics.featureextractor.RadiomicsFeatureExtractor(
        **settings)

    # Disable all features and enable the specified feature class
    extractor.disableAllFeatures()
    extractor.enableFeatureClassByName(feature_class)

    # Extract radiomics features using the extractor
    feature_vector = extractor.execute(image, mask)

    # Convert NumPy arrays to float in the feature vector
    for key in feature_vector.keys():
        if isinstance(feature_vector[key], np.ndarray):
            feature_vector[key] = float(feature_vector[key])

    return feature_vector


def extract_radiomics_features(image, mask, region_classes, feature_classes):
    """
    Extract radiomics features for different region and feature classes.

    Parameters:
        image (SimpleITK.Image): Input image.
        mask (SimpleITK.Image): Input mask.
        region_classes (list): List of region class names.
        feature_classes (list): List of feature class names.

    Returns:
        feature_vectors (dict): Dictionary containing extracted radiomics feature vectors.
    """
    # Cast the input mask to ensure consistent type
    mask = sitk.Cast(mask, sitk.sitkUInt8)

    # Set mask's direction and origin to match the image
    mask.SetDirection(image.GetDirection())
    mask.SetOrigin(image.GetOrigin())

    # Convert mask to a binary NumPy array
    mask_array = sitk.GetArrayFromImage(mask)
    mask_array = (mask_array > 0).astype(np.uint8)

    # Calculate nonzero slices from the mask
    nonzero_slices = np.nonzero(mask_array.sum(axis=(1, 2)))[0]

    # Dictionary to store feature vectors
    feature_vectors = {}

    for region_class in region_classes:
        if region_class == 'apex':
            slice_indices = nonzero_slices[0:math.floor(
                np.size(nonzero_slices) / 3)]
        elif region_class == 'base':
            slice_indices = nonzero_slices[np.size(
                nonzero_slices) - math.floor(np.size(nonzero_slices) / 3):]
        else:
            slice_indices = nonzero_slices

        # Combine the slices to create a 3D mask for the region
        new_mask_array = np.zeros_like(mask_array)
        new_mask_array[slice_indices] = mask_array[slice_indices]

        # Create a new mask image from the corrected mask array
        new_mask = sitk.GetImageFromArray(new_mask_array)
        new_mask.CopyInformation(mask)  # Copy image information to new mask

        for feature_class in feature_classes:
            # Extract radiomics features for the current region and feature class
            feature_vector = extract_features(image, new_mask, feature_class)

            # Store the feature vector in the dictionary
            key = f"{region_class}_{feature_class}"
            feature_vectors[key] = feature_vector

    return feature_vectors


def extract_filtered_values(extracted_features):
    """
    Extract and filter values from the extracted_features dictionary.

    Parameters:
        extracted_features (dict): Dictionary containing extracted radiomics feature vectors.

    Returns:
        values_array (numpy.ndarray): Numpy array containing corresponding values of the filtered variables.
    """
    # Iterate through each feature vector and exclude variables containing "diagnostics"
    for key in extracted_features:
        extracted_features[key] = {var_key: var_value for var_key,
                                   var_value in extracted_features[key].items() if "diagnostics" not in var_key}

    # Create an array containing the corresponding values of the filtered variables
    values_array = []
    for value in extracted_features.values():
        for var_value in value.values():
            values_array.append(var_value)

    # Convert the list of values into a numpy array
    values_array = np.array(values_array)

    return values_array


def read_coef_array_from_json(json_file_name):
    """
    Read a MATLAB coef array from a JSON file and convert it to a Python list.

    Parameters:
        json_file_name (str): The name of the JSON file containing the MATLAB array.

    Returns:
        coef_list (list): A Python list containing the data from the MATLAB array.
    """
    try:
        # Read the JSON file
        with open(json_file_name, 'r') as json_file:
            json_data = json.load(json_file)

        # Convert the JSON data back to a Python list
        coef_list = json_data

        return coef_list

    except FileNotFoundError:
        raise FileNotFoundError(f"File '{json_file_name}' not found.")
    except json.JSONDecodeError:
        raise ValueError(
            f"Unable to decode JSON data from '{json_file_name}'. Make sure the file contains valid JSON.")


def calculate_quality_score(predictors, coefs, intercept):
    """
    Calculate the quality score using given predictors, coefficients, and intercept.
    Caps the result between 0 and 100.

    Parameters:
        predictors (list): List of predictor values.
        coefs (list): List of corresponding coefficients.
        intercept (float): Intercept value.

    Returns:
        capped_quality_score (float): Calculated and capped quality score.
    """
    # Convert predictors list to a NumPy array
    predictors_array = np.array(
        predictors)

    # Convert coefficients list to a NumPy array
    coefs_array = np.array(coefs)

    # Calculate the quality score using dot product and add the intercept
    quality_score = np.dot(predictors_array, coefs_array) + intercept

    # Cap the quality score between 0 and 100
    capped_quality_score = max(0, min(quality_score, 100))

    return capped_quality_score


def classify_quality(quality_score, quality_class_threshold):
    """
    Classify the quality based on a given score and threshold.

    Parameters:
        quality_score (float): Quality score to classify.
        quality_class_threshold (float): Threshold for classification.

    Returns:
        quality_class (str): Classification result ("Acceptable" or "NOT Acceptable").
    """
    if quality_score < quality_class_threshold:
        quality_class = "NOT Acceptable"
    else:
        quality_class = "Acceptable"

    return quality_class
