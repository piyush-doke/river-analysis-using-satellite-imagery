# Modules to import -------------------------------------------------------------------------------
import os
import cv2
import math
import base64
from matplotlib import pyplot as plt
from river import River
from skeleton import Skeleton
from scan import Scan
# -------------------------------------------------------------------------------------------------


# Global Variables --------------------------------------------------------------------------------
rgbRED=[255.0,0.0,0.0]
rgbBLUE=[0.0,0.0,255.0]
rgbGREEN=[0.0,255.0,0.0]
rgbYELLOW=[255.0,255.0,0.0]
rgbBLACK=[0.0,0.0,0.0]
rgbWHITE=[255.0,255.0,255.0]
rgbCYAN=[0.0,255.0,255.0]
rgbSAFFRON=[255.0,128.0,0]
rgbPINK=[255.0,192.0,0]
# -------------------------------------------------------------------------------------------------


# The main fucntion -------------------------------------------------------------------------------
# Initialize the variables --------------------------------------------------------------
thresh = 0
scale = 1
interval_distance = 200
len_dang_arcs = 100
l_r_error = 8
final_average_width = 0
# ---------------------------------------------------------------------------------------


name1 = input('Give the name of the image (with the extension) : ')
scale = int(input('Give the scale of the image (how much distance 1 pixel maps onto the land) : '))
interval_distance = math.floor(int(input('Till what distance do you wish to find the isolated land patches : '))/scale)
thresh = int(input('Please specify a threshold value (enter 0 to find the threshold automatically) : '))
len_dang_arcs = math.floor(100/scale)


# Load the image into a cv2.imread() variable, in grey scale mode -----------------------
img = cv2.imread(name1,0)
# ---------------------------------------------------------------------------------------


# Calculate the average width -----------------------------------------------------------
river = River(img,thresh,math.floor(interval_distance/scale),0) # process the river image
skeleton = Skeleton(river,math.floor(len_dang_arcs/scale),0) # find the skeleton, junctions and reaches
scan = Scan(river,skeleton,l_r_error) # create a new Scan type object and run Compute() on it 
scan.Compute()

l2_stream = scan.getAllStreamFromReach(scan.l_reaches) # create a list of all the lists of stream points
scan.averageCalculation(math.floor(interval_distance/scale),l2_stream) # calculate the average width of the river (section by section also)
final_average_width = scan.average_width_river # store the average width into the variable - final_average_width

print(final_average_width*scale, " <- Average width of the river")
# ---------------------------------------------------------------------------------------


# Write the details to the text file ----------------------------------------------------
details='---------- This file contains the details of the river image analysed ----------\n\n\n'
details+='Threshold value used : '+str(river.threshold_value)+'\n'
details+='Scale value used : '+str(scale)+'\n'
details+='Interval distance selected : '+str(interval_distance)+'\n'
details+='Length of permissible dangling segments : '+str(len_dang_arcs)+'\n'
details+='Number of junctions : '+str(len(skeleton.list_Junction)-2)+'\n'
details+='Number of reaches : '+str(len(skeleton.l_Reach)-1)+'\n'
details+='Average width of the river : '+str(scan.average_width_river*scale)+'\n\n\n'
details+='Data about the sections ----------------------------------------\n\n'
for x in range(len(scan.l_average_width_section)):
	details+='Section '+str(x+1)+' -------------------------\n'
	details+='     Starting Distance : '+str(x*interval_distance)+'\n'
	details+='     Number of channels : '+str(scan.l_channels[x])+'\n'
	details+='     Average width : '+str(scan.l_average_width_section[x]*scale)+'\n\n'

with open('output.txt', 'w') as write_file :
	write_file.write(details)
# ---------------------------------------------------------------------------------------


# Display the reference image -----------------------------------------------------------
a_Image = scan.getNullFigure() # create a figure with all of its pixels - 0
a_Image.fill(255) # fill all the pixels with - 1

scan.drawRiverContour(a_Image,rgbBLUE) # draw the river contours
scan.drawSkeleton(a_Image,rgbBLACK,rgbBLACK) # draw the skeleton
scan.drawJunction(a_Image,rgbRED) # draw the junctions
scan.drawStream(a_Image,l2_stream,rgbGREEN) # draw the green lines across all stream points

plt.figure(1) # create a new figure
plt.imshow(a_Image) # draw a_Image on the current figure
plt.show() # display the figure
# ---------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------
