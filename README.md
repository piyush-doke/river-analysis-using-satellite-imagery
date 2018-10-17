# River-Analysis-using-Satellite-Imagery
I have developed a python program which analyzes various river features given a satellite image of that river, mainly the width of the river.

NOTE - This code is meant for python 3

## About the files and folder
- Documentation file contains all the information of the algorithm and the python libraries used
- PythonApplication1.py is the main file that should be run
- Output_details.txt contains the result of the analysis
- Rest of the python contain different classes and functions
- Temp folder contains the intermediate images that were generated during the process
- Test_Images folder contains some sample images to test the code

## How to run the code
- Using the terminal we run the python file - PythonApplication.py
- The code will then prompt the user for the following parameters:
  1. Name - Name of the river image file, the file should be in the same folder as that of the code.
  2. Scale - The size on land which is represented by one pixel in the image (set this as one for calculating the width of the river in pixels unit).
  3. Interval distance - information about the image is calculated in sections, this is the length of each section.
  4. Threshold - please refer to the documentation for more information regarding this (this can be set to 0, the algorithm will then automatically detect the correct value).

## Output
- The width of the river (displayed on the teminal), the unit of this calculation is governed by the value of scale
- The code creates on output file - Output_details.txt, this contains all the analysis results in detail
