from pyAutoRef import autoref
from pyPSQC.utils import read_sitk_image


def prepare_data(input_image_path, input_mask_path, input_normalized=False):
    """
    Prepare input data by optionally normalizing the image and reading the mask.

    Parameters:
        input_image_path (str): The file path to the input 3D image (any supported SimpleITK format) or to the DICOM folder.
        input_mask_path (str): Path to the corresponding mask of the input 3D image. Any supported SimpleITK format or DICOM folder.
        input_normalized (bool, optional): Whether the input image is normalized. Default is False.

    Returns:
        image (SimpleITK.Image): The SimpleITK image object representing the image.
        mask (SimpleITK.Image): The SimpleITK image object representing the mask.
    """
    # Check if the input is normalized
    if input_normalized:
        # Read input image and mask
        image = read_sitk_image(input_image_path)
        mask = read_sitk_image(input_mask_path)

    else:
        # Normalize the input image using AutoRef (fat and muscle)
        image = autoref(input_image_path)
        # Read the mask
        mask = read_sitk_image(input_mask_path)

    # Return the prepared image and mask
    return image, mask
