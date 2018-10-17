# Modules to import -------------------------------------------------------------------------------
import cv2
import copy
import numpy as npy
from scipy import ndimage
from matplotlib import pyplot as plt
# -------------------------------------------------------------------------------------------------

# Global Variables --------------------------------------------------------------------------------
BLUE=100
BLACK=0
WHITE=255
# -------------------------------------------------------------------------------------------------

# Class - River -----------------------------------------------------------------------------------
class River:
	# Class variables -------------------------------------------------------------------
	seedx=0 # x coordinate of a point in the river
	seedy=0 # y coordinate of a point in the river
	threshold_value=0 # threshold value, to threshold the greyscale image
	array_Image=[] # array to contain the image
	array_Boundary=[] # array to contain the boundary of the image
	contours=[] # array to contain the contours of the river
	row=0 # number of rows of the image array
	col=0 # number of columns of the image array
	rawImage=[] # array to contain the raw image
	list_of_sections_of_isolated_land_area=[] # list of lists to store the information of all the isolated land areas, section by section
	flag_fast=0 # if flag_fast is set to 1, then the class performs only fast functions
	# -----------------------------------------------------------------------------------

	# Constructor function --------------------------------------------------------------
	def __init__(self,img,threshVal,interval_distance,fast):
		# Initialize the variables
		self.seedx=0
		self.seedy=0
		self.threshold_value=0
		self.array_Image=[]
		self.array_Boundary=[]
		self.contours=[]
		self.row=0
		self.col=0
		self.rawImage=[]
		self.list_of_sections_of_isolated_land_area=[]
		self.flag_fast=fast

		# Perform some operations on the river
		# By the end of this constructor function we have the array_Image (numpy array), filled with 0 (Black) for land and 100 (blue) for water

		# 1. Performing some pre-processing on the image ----------------------
		print ("Preprocessing...")
		self.ImagePreProcessing(img,threshVal)

		# 2. Close the boundary -----------------------------------------------
		print ("Closing the boundaries")
		self.CloseBoundary()

		# 3. Remove the rotation introduced area ------------------------------
		print ("Floodfilling the outer area")
		self.RemoveOuterArea()

		# 4 Detect a seed point -----------------------------------------------
		print ("Choosing a seed point")
		self.IdentifySeedPoint()
		print ("     (",self.seedx,", ",self.seedy,")", " <- choosen seed point", sep="")

		# 5. Paint the river blue ---------------------------------------------
		print ("Painting the river blue")
		self.IdentifyRiver()

		if not fast:
			# 6. Remove isolated water patches --------------------------------
			print ("Connecting distinct river parts")
			print ("Removing unwanted isolated patches of water")
			self.RemoveIsolatedWaterArea()

			# 7. Find isolated land patches -----------------------------------
			print ("Finding isolated patches of land")
			self.FindIsolatedLandArea(interval_distance)
		return
	# -----------------------------------------------------------------------------------


	# Class Functions -------------------------------------------------------------------
	# Do some pre-processing on the image provided ----------------------------
	def ImagePreProcessing(self,img,threshVal):
		'''This function does some preprocessing in the self.array_Image.
		'''	
		self.rawImage = copy.copy(img)
		img = cv2.GaussianBlur(img,(5,5),0) # smooth self.array_Image using gaussian filter
		img = cv2.equalizeHist(img) # histogram equalization
		self.RotateAndCrop(img,threshVal) # binarize, rotate and crop the self.array_Image
		(self.row,self.col)=self.array_Image.shape # update the number of row and column count
		return
	# -------------------------------------------------------------------------


	# Rotate and crop the image -----------------------------------------------
	# and paint the river - white, land - black and rotation introduced area - white
	def RotateAndCrop(self,img,threshVal):

		# check if the user wants the code to find the threshold value automatically, if user passes 0
		if threshVal==0:
			threshVal, self.array_Image = cv2.threshold(img,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU) # create a binary image of the origanl image, by automatically finding the threshold value
			threshVal=threshVal//3+1
		
		self.threshold_value=threshVal # store the threshold value
		print("    ", threshVal, "<- threshold value used")

		# this makes the river color dark and land color light 
		ret, self.array_Image = cv2.threshold(img,threshVal,255,cv2.THRESH_BINARY) # create a binary image of the origanl image by using the threshold value
		# ---------------------------------------------------------------------
		# image after thresholding
		plt.imshow(self.array_Image)
		plt.savefig('temp/1_Threshold.png', format = 'jpg', dpi=1200)
		# ---------------------------------------------------------------------

		list_rotate=[]
		_, self.contours, hierarchy = cv2.findContours(self.array_Image,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE) # get contours for the above binary image	
		for cnt in self.contours: # for each contour
			rect = cv2.minAreaRect(cnt) # bound the contour using rectangle with minuimum area (may be rotated)
			list_rotate.append(rect[2]) # append its angle of rotation to the list

		median = npy.median(list_rotate) # take the median of the angle of rotation
		img = ndimage.rotate(img, -1 * median) # rotate the real image by that angle
		self.rawImage = ndimage.rotate(self.rawImage, -1 * median) # rotate the raw image also
		ret, self.array_Image = cv2.threshold(img,threshVal,255, cv2.THRESH_BINARY) # create a binary image of the rotated image
		self.array_Boundary = copy.deepcopy(self.array_Image) # create and store its shallow copy in array_Boundary
		_, self.contours, hierarchy = cv2.findContours(self.array_Boundary,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE) # get coutours for the rotated binary image
		# ---------------------------------------------------------------------
		# image after thresholding and rotation
		plt.imshow(self.array_Image)
		plt.savefig('temp/2_Threshold_Rotate.png', format = 'jpg', dpi=1200)
		# ---------------------------------------------------------------------

		l_topLefty,l_topLeftx=[],[]
		l_botRighty,l_botRightx=[],[]
		for cnt in self.contours: # for each contour
			x,y,w,h = cv2.boundingRect(cnt) # bound the countour using a rectangle
			# store its top left and bottom right coordinates
			l_topLefty.append(y)
			l_topLeftx.append(x)
			l_botRighty.append(y+h)
			l_botRightx.append(x+w)

		topLeft = (min(l_topLeftx)+5,min(l_topLefty)+5) # get the minimum of x and y coordinates of all top left points of the contour bounding rectangles
		botRight = (max(l_botRightx)-5,max(l_botRighty)-5) # get the maximum of x and y coordinates of all bottom right points of the contour bounding rectangles
		self.array_Image = self.array_Image[topLeft[1]:botRight[1],topLeft[0]:botRight[0]] # crop the binary image
		self.rawImage = self.rawImage[topLeft[1]:botRight[1],topLeft[0]:botRight[0]] # crop the raw image also
		# ---------------------------------------------------------------------
		# image after thresholding, rotation and cropping 
		plt.imshow(self.array_Image)
		plt.savefig('temp/3_Threshold_Rotate_Crop.png', format = 'jpg', dpi=1200)
		# ---------------------------------------------------------------------
		
		print ("     ", topLeft, ", ", botRight, " <- coordinates to crop (top-left and bottom-right)", sep="") # print the top-left and bottom-right coordintes ie. the cropping points 
		self.row,self.col = self.array_Image.shape # update the number of row and column count
		
		# this makes the river color light and land color dark 
		ret, self.array_Image = cv2.threshold(self.array_Image,threshVal,255, cv2.THRESH_BINARY_INV) # inverse threshold the binary image after cropping it (inverse its colors)
		# ---------------------------------------------------------------------
		# image after thresholding, rotation, cropping and color inversion
		plt.imshow(self.array_Image)
		plt.savefig('temp/4_Threshold_Rotate_Crop_Threshold.png', format = 'jpg', dpi=1200)
		# ---------------------------------------------------------------------		
		return
	# -------------------------------------------------------------------------


	#  Draw a boundary around the rotated image -------------------------------
	def CloseBoundary(self):
		'''This function draws a rectangle around the self.array_Image.
		Important for floodfill to work.
		'''
		# Bounding the image from the top left corner -------------------------
		flag = False
		# find the first black point starting from the top left corner:
		# 1. which is incident on the left edge of the bounding rectangle
		for i in range(self.col): # traverse down through a column then moving to the next column
			for j in range(self.row):
				if self.array_Image[j][i]==BLACK:
					x1=i
					y1=j
					flag=True
					break
			if flag:
				flag=False
				break
		# 2. which is incident on the top edge of the bounding rectangle
		for i in range(self.row): # traverse right though a row then moving to the next row
			for j in range(self.col):
				if self.array_Image[i][j]==BLACK:
					x2=j
					y2=i
					flag=True
					break
			if flag:
				flag=False
				break
		cv2.line(self.array_Image,(x1,y1),(x2,y2),BLACK) # draw a line joining these two points

		# Bounding the image from the top right corner ------------------------
		# find the first black point starting from the top right corner:
		# 1. which is incident on the right edge of the bounding rectangle
		for i in range(self.col-1,-1,-1): # traverse down through a column then moving to the previous column
			for j in range(self.row):
				if self.array_Image[j][i]==BLACK:
					x1=i
					y1=j
					flag=True
					break
			if flag:
				flag=False
				break
		# 2. which is incident on the top edge of the bounding rectangle
		for i in range(self.row): # traverse left though a row then moving to the next row
			for j in range(self.col-1,-1,-1):
				if self.array_Image[i][j]==BLACK:
					x2=j
					y2=i
					flag=True
					break
			if flag:
				flag=False
				break
		cv2.line(self.array_Image,(x1,y1),(x2,y2),BLACK) # draw a line joining these two points

		# Bounding the image from the bottom left corner ----------------------
		# find the first black point starting from the bottom left corner:
		# 1. which is incident on the left edge of the bounding rectangle
		for i in range(self.col): # traverse up through a column then moving to the next column
			for j in range(self.row-1,-1,-1):
				if self.array_Image[j][i]==BLACK:
					x1=i
					y1=j
					flag=True
					break
			if flag:
				flag=False
				break
		# 2. which is incident on the bottom edge of the bounding rectangle
		for i in range(self.row-1,-1,-1): # traverse right though a row then moving to the previous row
			for j in range(self.col):
				if self.array_Image[i][j]==BLACK:
					x2=j
					y2=i
					flag=True
					break
			if flag:
				flag=False
				break
		cv2.line(self.array_Image,(x1,y1),(x2,y2),BLACK) # draw a line joining these two points

		# Bounding the image from the bottom right corner ---------------------
		# find the first black point starting from the bottom right corner:
		# 1. which is incident on the right edge of the bounding rectangle
		for i in range(self.col-1,-1,-1): # traverse up through a column then moving to the previous column
			for j in range(self.row-1,-1,-1):
				if self.array_Image[j][i]==BLACK:
					x1=i
					y1=j
					flag=True
					break
			if flag:
				flag=False
				break
		# 2. which is incident on the bottom edge of the bounding rectangle
		for i in range(self.row-1,-1,-1): # traverse left though a row then moving to the previous row
			for j in range(self.col-1,-1,-1):
				if self.array_Image[i][j]==BLACK:
					x2=j
					y2=i
					flag=True
					break
			if flag:
				break
		cv2.line(self.array_Image,(x1,y1),(x2,y2),BLACK) # draw a line joining these two points
		# ---------------------------------------------------------------------
		# image after applying the boundaries
		plt.imshow(self.array_Image)
		plt.savefig('temp/5_Close_Boundary.png', format = 'jpg', dpi=1200)
		# ---------------------------------------------------------------------
		return
	# -------------------------------------------------------------------------


	# Paint the rotation introduced area black --------------------------------
	def RemoveOuterArea(self):
		'''This function floodfills the outer area of the image black (area introduced due to rotation).
		Finally we get an self.array_Image where only the river area is white.
		'''
		diff = (6,6,6)
		mask = npy.zeros((self.row+2, self.col+2), npy.uint8) # create a mask of dimensions +2 (numpy array with all elements initialized to zero) 
		cv2.floodFill(self.array_Image,mask,(2,2),BLACK,diff,diff) # flood fill the outer area into a dark color starting from all four corners
		cv2.floodFill(self.array_Image,mask,(0,self.row-2),BLACK,diff,diff)
		cv2.floodFill(self.array_Image,mask,(self.col-2,0),BLACK,diff,diff)
		cv2.floodFill(self.array_Image,mask,(self.col-2,self.row-2),BLACK,diff,diff)
		# ---------------------------------------------------------------------
		# image after removing the outer white, introduced due to rotation
		plt.imshow(self.array_Image)
		plt.savefig('temp/6_RemoveOuterArea.png', format = 'jpg', dpi=1200)
		# ---------------------------------------------------------------------
		return
	# -------------------------------------------------------------------------


	# Identify a seed point ---------------------------------------------------
	def IdentifySeedPoint(self):
		'''This function detects a seed point of the river.
		It repeatedly floodfills white pixels, and keeps track of the seed point which floodfills the maximum area.
		Because this maximum area will always be the river.
		'''
		copy_of_array_Image = copy.deepcopy(self.array_Image) # create a temporary copy of the binary Image stored in the numpy array - array_Image
		diff = (6,6,6)
		max = 0
		for i in range(self.row):
			for j in range(self.col):
				if (copy_of_array_Image[i][j]==WHITE): # for each white pixel (isolated water pixel)
					mask = npy.zeros((self.row+2, self.col+2), npy.uint8) # create a mask of dimensions +2 (numpy array with all elements initialized to zero) 
					cv2.floodFill(copy_of_array_Image, mask,(j,i), BLUE, diff, diff) # floodfill using that point as a seed point

					unique_elements, counts = npy.unique(mask, return_counts=True) # get the counts of 0's and 1's in the mask array
					# unique will be a sorted list of all the distinct elements in the numpy array - mask
					# counts will store the number of occurances of each of these unique elements
					if counts[1]>max: # check if the number of points that were floodfilled are greater than max
						max=counts[1] # if yes, then update max, seedx, seedy accordingly
						self.seedx=j
						self.seedy=i
		return
	# -------------------------------------------------------------------------


	# Paints the river blue leaving isolated water patches white --------------
	def IdentifyRiver(self):
		'''We paint the river with a BLUE self.color.
		One point of the river (self.seedx,self.seedy) called the "seed point" is used for this purpose.
		'''
		diff = (6,6,6)
		mask = npy.zeros((self.row+2, self.col+2), npy.uint8)
		cv2.floodFill(self.array_Image, mask,(self.seedx,self.seedy), BLUE, diff, diff)
		# ---------------------------------------------------------------------
		# image after painting the river blue
		plt.imshow(self.array_Image)
		plt.savefig('temp/7_IdentifyRiver.png', format = 'jpg', dpi=1200)
		# ---------------------------------------------------------------------
		return
	# -------------------------------------------------------------------------


	# Removes isolated water patches ------------------------------------------
	# paints the isolated white water patches black if they are away for the river
	# blue otherwise
	def RemoveIsolatedWaterArea(self):
		'''We remove the isolated water patches. 
		That is river points which lie nearby are connected.
		'''
		mask = npy.zeros((self.row+2, self.col+2), npy.uint8)
		diff = (6,6,6)

		for i in range(self.row):
			for j in range(self.col):
				if (self.array_Image[i][j]==WHITE): # for each white pixel (isolated water pixel)
					flag=0
					for k in range(-3,4): # check if any pixel in its neighbour hood has a blue pixel
						for l in range(-3,4):
							if (i+k<0 or i+k>=self.row or j+l<0 or j+l>=self.col): continue
							if (self.array_Image[i+k][j+l]==BLUE): # if blue pixel is found, floodfill that water patch blue
								cv2.floodFill(self.array_Image, mask,(j,i), BLUE, diff, diff)
								cv2.line(self.array_Image,(j,i),(j+l,i+k),(BLUE))
								flag=1
								break
						if flag==1: break
					if flag==0:
						cv2.floodFill(self.array_Image,mask,(j,i),BLACK,diff,diff) # if not, floodfill that water patch black
		# ---------------------------------------------------------------------
		# image after removing the isolated water patches
		plt.imshow(self.array_Image)
		plt.savefig('temp/8_RemoveIsolatedWaterArea.png', format = 'jpg', dpi=1200)
		# ---------------------------------------------------------------------
		return
	# -------------------------------------------------------------------------


	# Find isolated land patches ----------------------------------------------
	def FindIsolatedLandArea(self,interval_distance):
		'''We find the isolated land patches, by painting the outer land blue, which give us the isolated patches of land in black.
		And we store them section by section in the list - list_of_sections_of_isolated_land_area.
		'''
		# making outer land and river the same color --------------------------
		diff = (6,6,6)
		copy_of_array_Image = copy.deepcopy(self.array_Image) # create a temporary copy of the binary Image stored in the numpy array - array_Image
		mask = npy.zeros((self.row+2, self.col+2), npy.uint8) # create a mask of dimensions +2 (numpy array with all elements initialized to zero) 
		cv2.floodFill(copy_of_array_Image,mask,(2,2),BLUE,diff,diff) # flood fill the outer area into blue color starting from all four corners
		cv2.floodFill(copy_of_array_Image,mask,(0,self.row-2),BLUE,diff,diff)
		cv2.floodFill(copy_of_array_Image,mask,(self.col-2,0),BLUE,diff,diff)
		cv2.floodFill(copy_of_array_Image,mask,(self.col-2,self.row-2),BLUE,diff,diff)

		# marking the different sections --------------------------------------
		for i in range(0,self.row,interval_distance): # mark the sections using blue lines with the interval equal to - interval_distance
			cv2.line(copy_of_array_Image,(0,i),(self.col,i),BLUE) # draw a line joining these two points
		# ---------------------------------------------------------------------
		# image after identifying the isolated land patches
		plt.imshow(copy_of_array_Image)
		plt.savefig('temp/9_FindIsolatedLandArea.png', format = 'jpg', dpi=1200)
		# ---------------------------------------------------------------------

		# storing the required isolated land patches --------------------------
		l_isolated_land_area_in_a_section=[]
		temp_interval_distance=interval_distance
		for i in range(self.row):
			# if we pass the interval line, we enter a new section
			if i>temp_interval_distance:
				self.list_of_sections_of_isolated_land_area.append(l_isolated_land_area_in_a_section) # append the list - l_isolated_land_area_in_a_section, to the list - list_of_sections_of_isolated_land_area
				l_isolated_land_area_in_a_section=[] # empty the list of isolated land areas in the current section
				temp_interval_distance+=interval_distance # calculate the next interval line

			# if we are on the interval line, skip the ith iteration
			elif i==temp_interval_distance:
				break

			for j in range(self.col): # for each pixel (i,j)
				# if we find a black pixel (isolated land pixel)
				if (copy_of_array_Image[i][j]==BLACK):
					mask = npy.zeros((self.row+2, self.col+2), npy.uint8) # create a mask of dimensions +2 (numpy array with all elements initialized to zero) 
					cv2.floodFill(copy_of_array_Image, mask,(j,i), BLUE, diff, diff) # flood that patch with blue
					
					unique_elements, counts = npy.unique(mask, return_counts=True) # get the counts of 0's and 1's in the mask array
					counts[1]-=2*self.row+2*self.col+4 # eliminate the error introduced due to the larger (+2) dimensions of the mask
					l_isolated_land_area_in_a_section.append([counts[1], mask]) # store the number of pixels in that patch and the mask as a list of two elements in the list - l_isolated_land_area_in_a_section
		
		# storing the last section of isolated land areas
		self.list_of_sections_of_isolated_land_area.append(l_isolated_land_area_in_a_section) # append the list - l_isolated_land_area_in_a_section, to the list - list_of_sections_of_isolated_land_area
		return
	# -------------------------------------------------------------------------


	# Return the image (blue and black) stored in self.array_Image ------------
	def getRiver(self):
		return self.array_Image
	# -------------------------------------------------------------------------


	# Find the boundary of the river ------------------------------------------
	# and store it in the numpy array - array_Boundary
	def getContour(self):
		self.array_Boundary = copy.deepcopy(self.array_Image) # create a shallow copy of the numpy array - array_Image, and store it in array_Boundary
		_, self.contours, hierarchy = cv2.findContours(self.array_Boundary,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE) # get contours for the image stored in the numpy array - array_Boundary
		
		self.array_Boundary=npy.zeros((self.row,self.col,3),npy.uint8) # fill the numpy array - array_Boundary, with zeros
		cv2.drawContours(self.array_Boundary,self.contours, -1, (0,0,255), 1) # draw countours in the numpy array - array_Boundary
		return
	# -------------------------------------------------------------------------


	# Check if the point belongs to the river boundary ------------------------
	def isBoundary(self,i,j):
		if npy.array_equal(self.array_Boundary[i][j],(0,0,255)):
			return True
		return False
	# -------------------------------------------------------------------------


	# Check if the point belongs to the river ---------------------------------
	def isRiver(self,x,y):
		if (self.array_Image[x][y]>0): return True
		return False
	# -------------------------------------------------------------------------


	# Draw the river contours -------------------------------------------------
	def drawContours(self,a_Image,rgb_color):
		cv2.drawContours(a_Image,self.contours, -1, rgb_color, 1)
		return
	# -------------------------------------------------------------------------
	# -----------------------------------------------------------------------------------





	# Not Needed ------------------------------------------------------------------------
	"""
	def getRGBRawImage(self):
		cmap = plt.get_cmap('jet') # for colured images
		rgba_img = cmap(self.rawImage)
		# rgb_img = npy.delete(rgba_img, 3, 2)
		return rgba_img
		# cmap = plt.get_cmap('gray')
		# rgba_img = cmap(self.rawImage)
		# rgb_img = npy.delete(rgba_img, 3, 2)
		# rgb_img = cv2.cvtColor(rgb_img, cv.CV_GRAY2RGB)
		# return rgb_img

	'''
	def rgb2gray(rgb):
		r,g,b = rgb[:,:,1], rgb[:,:,2], rgb[:,:,3]
		gray = 0.2989*r + 0.5870 * g + 0.1140 * b
		return gray
	'''

	def Draw(self,i):
		plt.figure(i)
		plt.imshow(self.array_Image)
		return
	"""
# End of class ------------------------------------------------------------------------------------
