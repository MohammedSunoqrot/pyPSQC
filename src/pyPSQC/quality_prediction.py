import pkg_resources
from pyPSQC.utils import read_coef_array_from_json, calculate_quality_score, classify_quality


def quality_prediction(features_values, quality_class_threshold):
    """
    Predict quality score and classify based on given features and threshold.

    Parameters:
        features_values (list): List of feature values (predictors) for prediction.
        quality_class_threshold (float): Threshold for classification. It can be between [0 - 100].

    Returns:
        quality_score (float): Calculated and capped quality score. It represents a perecentage [min = 0%, max 100%].
        quality_class (str): Classification result ("Acceptable" or "NOT Acceptable").
    """
    # Read the trained LASSO model coefficients array from JSON file
    json_file_path = pkg_resources.resource_filename(
        __name__, "model_coef.json")
    json_file_name = json_file_path
    coefs = read_coef_array_from_json(json_file_name)

    # Set intercept value of the trained LASSO model
    intercept = -589.6493539841075

    # Predict the quality score by applying the equation
    quality_score = calculate_quality_score(features_values, coefs, intercept)
    quality_score = round(quality_score, 2)

    # Classify the quality score based on a given threshold
    quality_class = classify_quality(quality_score, quality_class_threshold)

    # Return the mask quality score and class
    return quality_score, quality_class
