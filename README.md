# Algorithm for River Analysis Using Satellite Imagery
A Python program which analyzes river features given a satellite image of that river.


## About the files and folder
- Documentation.docx contains detailed information on the algorithm and libraries used.
- PythonApplication1.py is the main file to be run.
- Output_details.txt will contain the result of the analysis performed.
- Temp folder contains the intermediate images that were generated during the run.
- Test_Images folder contains some sample images to test the code with.

## Instructions to Run
Run the python file - PythonApplication.py

## Inputs
- Name - Name of the river image file.
- Scale - The size on land which is represented by one pixel in the image (set this as 1, for calculating the width of the river in pixels unit).
- Interval distance - information about the image is calculated in sections, this parameter is used to fix the length of each such section.
- Threshold - please refer to the documentation for detailed information regarding this parameter (this can be set to 0 for auto detection).

## Outputs
- Width of the river is displayed after analysis whose unit is governed by the value of the scale.
- Code creates a file - Output_details.txt that contains in-depth results.
