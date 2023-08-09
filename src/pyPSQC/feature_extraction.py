from pyPSQC.utils import extract_radiomics_features, extract_filtered_values


def feature_extraction(image, mask):
    """
    Extract radiomics features for different region and feature classes.

    Parameters:
        image (SimpleITK.Image): Input image.
        mask (SimpleITK.Image): Input mask.

    Returns:
        features_values (numpy.ndarray): Numpy array containing corresponding values of the features.
    """
    # List of region classes and feature classes to extract
    region_classes = ['wholeprostate', 'apex', 'base']
    feature_classes = ['firstorder', 'shape',
                       'glcm', 'glrlm', 'glszm', 'ngtdm', 'gldm']

    # Extract radiomics features for the specified image and mask
    extracted_features = extract_radiomics_features(
        image, mask, region_classes, feature_classes)

    # Create an array containing the corresponding values of the extracted features
    features_values = extract_filtered_values(extracted_features)

    # Return filtered feature values
    return features_values
