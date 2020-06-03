# Implementation Guide
A Python program that analyzes river features from satellite imagery.


## About the files and folders
- Documentation.docx contains detailed information on the algorithm and libraries used.
- Temp folder is used to contain any intermediate images that were generated during the run.
- Test_Images folder contains some sample images to test the code with.

## Instructions to Run
Run the python file - PythonApplication.py

## Inputs
- Name - Name of the river image file.
- Scale - Actual size of land represented by one pixel in the image (set this to 1, for calculating the width in pixels).
- Interval distance - Information about the image is calculated in sections of equal length, this parameter is used to fix the length of each such section.
- Threshold - Please refer to documentation.docx for detailed information regarding this parameter (this can be set to 0 for auto-detection).

## Outputs
- Width of the river is displayed after analysis, where the unit is governed by the value of scale.
- Code creates Output_details.txt to contain in-depth results of the run.
