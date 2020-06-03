# River Analysis Using Satellite Imagery

## Objective

The average width of a river is crucial for calculating its discharge. But doing so for any point in time is difficult without chronological measurements, as temporal changes in river width are inevitable. Satellite imagery does a commendable job of preserving this historic data. And hence, a method compatible with this form of input was required.

NOTE: Created in Python 3.

## About the Repository
```
./river-analysis-using-satellite-imagery
├── docs
│   └── Documentation.docx                  # Documentation for the algorithm
├── temp                                    # To contain itermediate files generated during a run
│   └── ...
├── test_images                             # Contains sample images to test the code with
│   └── ...
├── README.md
├── __init__.py
├── junction.py
├── main.py
├── output.txt
├── reach.py
├── river.py
├── scan.py
├── skeleton.py
└── stream.py
```

## Instructions to Run
```
python main.py                              # Run the script using python 3
```

## Inputs
- Name - Path to the river image.
- Scale - Actual size of land represented by one pixel in the image (set this to 1 for calculating the width in pixels).
- Interval Distance - Analysis is done in sections of equal length, this parameter is used to fix the length of each such section.
- Threshold - Refer to [Documentation.docx](docs/Documentation.docx) for detailed information regarding this parameter (set this to 0 for auto-detection).

## Outputs
```
output.txt                                  # Analysis results are dumped here
```
