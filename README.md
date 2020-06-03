# Implementation Guide
A Python program that analyzes river features from satellite imagery.

NOTE: Created in Python 3.


## About the Repository
```
river-analysis-using-satellite-imagery/
|-- docs
    |-- documentation.docx
|-- 
|
```

## Instructions to Run
```
python3 main.py
```

## Inputs
- Name - Name of the river image file.
- Scale - Actual size of land represented by one pixel in the image (set this to 1, for calculating the width in pixels).
- Interval Distance - Information about the image is calculated in sections of equal length, this parameter is used to fix the length of each such section.
- Threshold - Please refer to documentation>Documentation.docx for detailed information regarding this parameter (this can be set to 0 for auto-detection).

## Outputs
```
output.txt
```
