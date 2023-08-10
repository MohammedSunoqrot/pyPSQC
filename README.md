![PyPI](https://img.shields.io/pypi/v/pyPSQC)
# pyPSQC
### Prostate Segmentation Quality Control System
**A quality control system for automated prostate segmentation on T2-weighted MRI**
This is the python version of the "A quality control system for automated prostate segmentation on T2-weighted MRI"

This is a fully automated quality control system that generate a quality score and class for assessing the accuracy of automated prostate segmentations on T2W MR imagese.

This fully automated quality control system employs radiomics features for estimating the quality of deep-learning based prostate segmentation on T2W MR images.
The performance of our system is developed and tested using two data cohorts and 4 different deep-learning based segmentation algorithms.

The method was developed at the CIMORe group at the Norwegian University of Science and Technology (NTNU) in Trondheim, Norway.
https://www.ntnu.edu/isb/cimore

For detailed information about this method, please read our paper: https://www.mdpi.com/2075-4418/10/9/714

# Note
The provided algorithm was developed for research use and was NOT meant to be used in clinic.

# Structure
```
pyPSQC/
├── LICENSE
├── pyproject.toml
├── README.md
├── setup.cfg
├── src/
│   └── pyPSQC/
│       ├── __init__.py
│       ├── psqc.py
│       ├── prepare_data.py
│       ├── feature_extraction.py
│       ├── quality_prediction.py
│       ├── utils.py
│       ├── MANIFEST.in
│       └── model_coef.json
```

# Installation
You can install the package either from pip or using pip or the files in GitHub repository https://github.com/MohammedSunoqrot/pyPSQC

## pip
Simply type:
```
pip install pyPSQC
```
## GitHub
- Clone the GitHub repository
  
   *From command line*
   ```
   git clone https://github.com/MohammedSunoqrot/pyPSQC.git
   ```
- Change directory to the clones folder (unzip if needed) and type
   ```
   pip install . 
   ```
# MATLAB version
This python version is translation the originally published MATLAB® version [https://github.com/ntnu-mr-cancer/SegmentationQualityControl].
If you want to use it in MATLAB®, check the repository. 

# How to cite the system/pyPSQC
In case of using or refering to this system/package, please cite it as:

Sunoqrot, M.R.S.; Selnæs, K.M.; Sandsmark, E.; Nketiah, G.A.; Zavala-Romero, O.; Stoyanova, R.; Bathen, T.F.; Elschot, M. A Quality Control System for Automated Prostate Segmentation on T2-Weighted MRI. *Diagnostics* **2020**,*10*, 714.
https://doi.org/10.3390/diagnostics10090714

# How to use pyPSQC
To use the system to predict a segmentation/mask quality score and class, you first need to import the `psqc` function.
You can do it by calling `from pyPSQC import psqc`

## `psqc` Function 
   - Parameters:
    - input_image_path (str): The file path to the input 3D image (any supported SimpleITK format) or to the DICOM folder.
    - input_mask_path (str): Path to the corresponding mask of the input 3D image. Any supported SimpleITK format or DICOM folder.
    - input_normalized (bool, optional): Whether the input image is normalized. Default is False.
    - quality_class_threshold (float, optional): Threshold for classifying quality. It can be between [0 - 100]. Default is 85. 

   - Returns:
    - quality_score (float): Calculated and capped quality score. It represents a perecentage [min = 0%, max 100%].
    - quality_class (str): Classification result ("Acceptable" or "NOT Acceptable").

## Important notes    
- **The quality_score represents a perecentage [min = 0%, max 100%]**
- **If the input image normalized (the method deigned to get images normalized with [AutoRef](https://github.com/MohammedSunoqrot/pyAutoRef)), Set `input_normalized`to `True`, otherwise skip it or set it to `False`**
- **The quality_class_threshold must be between 0-100. Ny default set to 85**

## Supported input/output formats
- DICOM Series.
- All the medical [images formats supported by SimpleITK](https://simpleitk.readthedocs.io/en/v2.2.0/IO.html).
- [SimpleITK.Image](https://simpleitk.org/SimpleITK-Notebooks/01_Image_Basics.html).

***DICOM Series is recognized when there is no file extension***

### Examples of usage:

***Example (image: medical image format, mask: medical image format):***
```
from pyPSQC import psqc

input_image_path = r"C:\Data\Case10_t2.nii.gz"
input_mask_path = r"C:\Data\Case10_t2_normalized_segmentation.nii.gz"
input_normalized = False
quality_class_threshold = 85

quality_score, quality_class = psqc(input_image_path, input_mask_path, input_normalized, quality_class_threshold)
```

***Example (image: medical image format, mask: DICOM Series):***
```
from pyPSQC import psqc

input_image_path = r"C:\Data\Case10_t2.nii.gz"
input_mask_path = r"C:\Data\Case10_t2_segmentation"
input_normalized = False
quality_class_threshold = 85

quality_score, quality_class = psqc(input_image_path, input_mask_path, input_normalized, quality_class_threshold)
```

***Example (image: DICOM Series, mask: medical image format):***
```
from pyPSQC import psqc

input_image_path = r"C:\Data\Case10_t2"
input_mask_path = r"C:\Data\Case10_t2_segmentation.nii.gz"
input_normalized = True
quality_class_threshold = 88

quality_score, quality_class = psqc(input_image_path, input_mask_path, input_normalized, quality_class_threshold)
```
***Example (image: DICOM Series, mask: DICOM Series):***
```
from pyPSQC import psqc

input_image_path = r"C:\Data\Case10_t2"
input_mask_path = r"C:\Data\Case10_t2_segmentation"
input_normalized = False
quality_class_threshold = 87

quality_score, quality_class = psqc(input_image_path, input_mask_path, input_normalized, quality_class_threshold)
```

# Retrain the system
If you want to retrain the sytem to fit your data better, you need to do it in MATLAB®. 
 
Follow the instructions in "Retrain". [https://github.com/ntnu-mr-cancer/SegmentationQualityControl/tree/master/Retrain]
There you will find a detailed desctiotion and all the codes you need to do the training. 

To update thi python package after retraining the system:
- Export `trainedModel.coef` to `model_coef.json` and replace this packge file `pyPSQC/src/pyPSQC/model_coef.json` with your new file.
    - This code can help you in the exportation:
    ```
    % Save the coefficients array as a JSON file
    jsonStr = jsonencode(trainedModel.coef);
    jsonFileName = 'model_coef.json';
    fid = fopen(jsonFileName, 'w');
    fprintf(fid, '%s', jsonStr);
    fclose(fid);
    disp(['Coefficients array saved as ' jsonFileName]);
    ```
- Get the `trainedModel.Intercept` value and replace the value of `intercept` in `pyPSQC/src/pyPSQC/quality_prediction.py` with it.

# Contact us
Feel free to contact us:
mohammed.sunoqrot@ntnu.no
