# Modules to import -------------------------------------------------------------------------------
import numpy as npy
from river import River
from reach import Reach
from skeleton import Skeleton
from junction import Junction
# from transect import Transect
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

# Class - Scan ------------------------------------------------------------------------------------
class Scan:
	# Class variables -------------------------------------------------------------------
	river=[] # store a River type variable
	skeleton=[] # store a Skeleton type variable
	l_junctions=[] # store a list of Junction type variables
	l_reaches=[] # store a list of Reach type variables
	left_right_error=0 # store the absolute permissible difference between the left and right green line
	l_channels=[] # store a list containing the number of channels for each section
	l_average_width_section=[] # store a list containing the average widths of the river for each section
	average_width_river=0 # store the total average width of the river
	# -----------------------------------------------------------------------------------

	# Constructor function --------------------------------------------------------------
	def __init__(self,river,skeleton,l_r_error):
		# Initialize the variables
		self.river=river
		self.skeleton=skeleton
		self.l_junctions=skeleton.list_Junction
		self.l_reaches=skeleton.l_Reach
		self.left_right_error=l_r_error
		self.l_channels=[0]
		self.l_average_width_section=[]
		self.average_width_river=0
		return
	# -----------------------------------------------------------------------------------


	# Class Functions -------------------------------------------------------------------
	# Compute all the data about stream points --------------------------------
	# also find the length and average width of all reaches
	def Compute(self):
		self.river.getContour() # run the function - getContour(), to find the boundary of the river

		# compute the average width across all stream points
		print ("Computing average width across all the stream points and reaches")
		for reach in self.l_reaches: # for each Reach type variable
			reach.computeDistance() # run the function - computeDistance(), on the given Reach variable
			l_stream=reach.getStreamList() # fetch the list of all stream points contained in that given reach
			for stream in l_stream: # for each stream point
				self.getAllInfo(stream) # run the function - getAllInfo(), on that stream point
			reach.ComputeAvgMean() # compute the average width of that given reach
		return
	# -------------------------------------------------------------------------


	# Calculate width and other data for the given stream point ---------------
	def getAllInfo(self,stream):
		i,j = stream.getLocation() # get the position of the current stream point
		# if the position is not part of the skeleton, return
		if not self.skeleton.isSkeleton(i,j): return

		# we now identify two points up(x,y) and down(x,y) on the skeleton using the function - getPerpPoint()
		# lets call them support points, and the point (i,j) the center point
		# we draw a perpendicular to the line joining the support points and passing through the center point
		topcoly,topcolx=self.getPerpPoint(i,j,+1)
		botcoly,botcolx=self.getPerpPoint(i,j,-1)
		# if the support points were not found, (-1,-1) was returned, do not calculate the width across it
		if (topcoly==-1) or (botcoly==-1): return

		tempx,tempy,tempx3,tempy3,m=0,0,0,0,0
		# if the support points are in a horizontal line
		if topcoly==botcoly:
			# if they are the center point (i,j) itself, do not calculate the width across it
			if topcolx==botcolx:
				return
			# if they are unique, find the boundary points
			else:
				# traverse up and down from the center point to find the boundary points
				tempy,tempx=self.getUpDownPoint(i,j,+1)
				tempy3,tempx3=self.getUpDownPoint(i,j,-1)

		# if the support points are not in a horizontal line
		else:
			# we identify a line perpendicular to the support points, but passing through (i,j)
			# m, c = slope, y-intercept
			m,c = self.getPerpendicularLine(topcolx,topcoly,botcolx,botcoly,j,i)
			# we now find out the boundary points using the center point, slope and y-intercept
			tempx,tempy = self.getBoundaryPoint(j,m,c,+1)
			tempx3,tempy3 = self.getBoundaryPoint(j,m,c,-1)

		# if the boundary points were not found in the getUpDownPoint() or getBoundaryPoint() function and (-1,-1) was returned, do not calculate the width across it
		if (tempx3<=0) or (tempx<=0): return
		# if the y coordinates of the boundary points are beyond the image, do not calculate the width across it
		if (tempy>=self.river.row-5) or (tempy3 >=self.river.row-5): return
		# check if the left and right boundary points are at a similar distance from the center point
		dist1=npy.sqrt((tempy3-i)**2+(tempx3-j)**2)
		dist2=npy.sqrt((tempy-i)**2+(tempx-j)**2)
		# if the distance is not similar, do not calculate the width across it
		if abs(dist1-dist2)>=self.left_right_error: return

		# formula for calculating width across the given stream point
		d=npy.sqrt((tempy3-tempy)**2+(tempx3-tempx)**2)

		# fill the information calculated, into the Stream type variable
		stream.setValues(d,m,(tempx,tempy),(tempx3,tempy3))
		return
	# -------------------------------------------------------------------------


	# Get support points around the given point -------------------------------
	# to draw a perpendicular to the line joining them
	def getPerpPoint(self,x,y,l):
		# if l is +1, find the skeleton point starting from the x-2th (top most) row, down to the xth row, traversing from left to right
		# if l is -1, find the skeleton point starting from the x+2th (bottom most) row, up to the xth row, traversing from right to left	
		for i in list(reversed(range(0,3))):
			for j in list(reversed(range(-2,3))):
				# return the required skeleton points
				if (self.skeleton.isSkeleton(x-l*i,y-l*j)>0): return (x-l*i,y-l*j)

		# if no such point is found, return (-1,-1)
		return -1,-1
	# -------------------------------------------------------------------------


	# Traverse up/down a given skeleton point to find its boundary points -----
	def getUpDownPoint(self,x,y,down):
		# if down = +1, we traverse down
		# if down = -1, we traverse up
		row = self.river.row
		i=x+down
		while (i<row) and (i>0):
			# while traversing up/down if a skeleton point is found (error), return (-1,-1)
			if self.skeleton.isSkeleton(i,y):
				return -1,-1
			# while traversing up/down if a boundary point is found, return its coordinates
			elif self.river.isBoundary(i,y):
				return i,y
			i=i+down
		# if nothing is found (error), return (-1,-1)
		return -1,-1
	# -------------------------------------------------------------------------


	# Find the slope and y-intercept of the perpendicular line ----------------
	def getPerpendicularLine(self,x1,y1,x2,y2,x0,y0):
		# returns the slope, m1 and constant c1 for the line perpendicular to (x1,y1),(x2,y2)
		# and this line passes through the point (x0,y0), the center point
		m1=float(float(x1-x2)/float(y2-y1))
		c1=y0-m1*x0
		return m1,c1
	# -------------------------------------------------------------------------


	# Get the boundary points -------------------------------------------------
	# that lie on line with the given slope, y-intercept and which through the center point
	def getBoundaryPoint(self,x3,m1,c1,right):
		# If right = +1, identify the right boundary of the river
		# if right = -1, identify the left boundary of the river
		col = self.river.col
		row = self.river.row

		# m1,c1 represent a line, whose one dimension is x3
		# its other dimension is found out and we draw the line towards the right or left
		while (x3<col-1) and (x3>0): # for each value of x-coordinate
			y3=int(m1*(x3)+c1) # calculate the y-coordinate using the equation

			# if we go out of bounds (error), return (-1,-1)
			if (y3>row-2) or (y3<1): return -1,-1

			# check, if the calculated point is a boundary point
			f,tempy,tempx = self.findRiverBoundary(y3,x3)

			# if the point is not a boundary point nor a river point (if we go past the river boundary)
			if (f==0) and (not self.river.isRiver(y3,x3)): f=1

			# if the required point is found, return its coordinates
			if f==1: return tempx,tempy

			x3=x3+right # increment the value of x3
		# if we go out of bounds (error), return (-1,-1)
		return -1,-1
	# -------------------------------------------------------------------------


	# Compute the average width of the river section by section ---------------
	# and also compute the total average width of the river
	def averageCalculation(self, interval_distance, lol_of_stream_points):


		













		# Compute the average width of the river per section ------------------
		print ("Computing average width of the river, section by section")
		temp_interval_distance=interval_distance
		l_widths_of_all_sections=[]
		l_widths_of_a_section=[]
		temp_channels=0
		temp_prev_channels=0
		flag=True
		# 1. by summing all widths in a line ----------------------------------
		"""
		for i in range(self.skeleton.row):
			width_sum=[0]
			# if we pass the interval line, we enter a new section
			if i>temp_interval_distance:
				temp_interval_distance+=interval_distance # calculate the next interval line
				self.l_channels.append(0) # append 0 to the list - self.l_channels
				l_widths_of_all_sections.append(l_widths_of_a_section) # append the list of widths of the previous section to the list - l_widths_of_all_sections
				l_widths_of_a_section=[] # empty the list - l_widths_of_a_section

			for j in range(self.skeleton.col): # for each pixel (i,j)
				# if (i,j) is a boundary pixel
				if self.river.isBoundary(i,j):
					flag=True
				# if (i,j) is a skeleton pixel
				if self.skeleton.isSkeleton(i,j):
					# if a boundary point was found before this skeleton point
					if flag:
						temp_channels+=1 # increment the number of channels found
						flag=False

					for x in range(len(lol_of_stream_points)):
						for y in range(len(lol_of_stream_points[x])): # for each stream point
							if lol_of_stream_points[x][y].point==[i,j]: # if we find this skeleton point (i,j) in the list of lists - lol_of_stream_points
								if lol_of_stream_points[x][y].width!=-1: # and if the width at this stream point was calculated
									width_sum.append(lol_of_stream_points[x][y].width) # append this width to the list - width_sum
			
			# if channels are found for the first time after entering a new section
			if self.l_channels[len(self.l_channels)-1]==0: self.l_channels[len(self.l_channels)-1]=temp_channels
			# if the number of channels found are greater than the number of channels found previously
			elif temp_channels>temp_prev_channels: self.l_channels[len(self.l_channels)-1]+=temp_channels-temp_prev_channels
			temp_prev_channels=temp_channels
			temp_channels=0
			flag=True

			# if nothing was appended in the list - width_sum, skip ahead
			if len(width_sum)<=1: continue
			# if something was appended, find the sum of the widths
			else: l_widths_of_a_section.append(sum(width_sum)) # append the sum to the list - l_widths_of_a_section

		l_widths_of_all_sections.append(l_widths_of_a_section) # append the list of widths of the last section to the list - l_widths_of_all_sections
		"""
		# ---------------------------------------------------------------------

		# 2. by summing widths of all individual stream points ----------------
		for i in range(self.skeleton.row):
			# if we pass the interval line, we enter a new section
			if i>temp_interval_distance:
				temp_interval_distance+=interval_distance # calculate the next interval line
				self.l_channels.append(0) # append 0 to the list - self.l_channels
				l_widths_of_all_sections.append(l_widths_of_a_section) # append the list of widths of the previous section to the list - l_widths_of_all_sections
				l_widths_of_a_section=[] # empty the list - l_widths_of_a_section

			for j in range(self.skeleton.col): # for each pixel (i,j)
				# if (i,j) is a river boundary pixel
				if self.river.isBoundary(i,j):
					flag=True
				# if (i,j) is a skeleton pixel
				if self.skeleton.isSkeleton(i,j):
					# if a boundary point was found before this skeleton point
					if flag:
						temp_channels+=1 # increment the number of channels found
						flag=False

					for x in range(len(lol_of_stream_points)):
						for y in range(len(lol_of_stream_points[x])): # for each stream point
							if lol_of_stream_points[x][y].point==[i,j]: # if we find this skeleton point (i,j) in the list of lists - lol_of_stream_points
								if lol_of_stream_points[x][y].width!=-1: # and if the width at this stream point was calculated
									l_widths_of_a_section.append(lol_of_stream_points[x][y].width) # append this width to the list - l_widths_of_a_section

			# if channels are found for the first time after entering a new section
			if self.l_channels[len(self.l_channels)-1]==0: self.l_channels[len(self.l_channels)-1]=temp_channels
			# if the number of channels found are greater than the number of channels found previously
			elif temp_channels>temp_prev_channels: self.l_channels[len(self.l_channels)-1]+=temp_channels-temp_prev_channels
			temp_prev_channels=temp_channels
			temp_channels=0
			flag=True

		l_widths_of_all_sections.append(l_widths_of_a_section) # append the list of widths of the last section to the list - l_widths_of_all_sections
		# ---------------------------------------------------------------------

		# calculating the average width of the river for each section, and store it in the list - self.l_average_width_section
		for i in range(len(l_widths_of_all_sections)):
			if len(l_widths_of_all_sections[i])!=0: self.l_average_width_section.append(sum(l_widths_of_all_sections[i])/len(l_widths_of_all_sections[i]))
			else: self.l_average_width_section.append(0)

		# Compute the total average width of the river ------------------------
		print ("Computing average width of the full river")
		counter=0
		# 1. by using reaches -------------------------------------------------
		"""
		for reach in self.l_reaches:
			if reach.avgWidth==-1: continue # if the average width of the reach was not calculated, skip this reach

			self.average_width_river+=reach.avgWidth # take summation of widths for all reaches left
			counter+=1 # increment the counter
		"""
		# ---------------------------------------------------------------------

		# 2. by using stream points -------------------------------------------
		for i in range(len(lol_of_stream_points)):
			for j in range(len(lol_of_stream_points[i])):
				if lol_of_stream_points[i][j].width==-1: continue # if the average width of the stream point was not calculated, skip this stream point

				self.average_width_river+=lol_of_stream_points[i][j].width # take summation of widths for all stream points left
				counter+=1 # increment the counter
		# ---------------------------------------------------------------------

		# if the number of valid 'reaches/stream_points' (a 'reach/stream_point' is valid is when the average width across it is not equal to -1), is more than 0
		if counter!=0: self.average_width_river=self.average_width_river/counter # compute the average
		return
	# -------------------------------------------------------------------------


	# Check if the given point is a boundary point ----------------------------
	def findRiverBoundary(self,x,y):
		if self.river.isBoundary(x,y): return 1,x,y
		return 0,x,y
	# -------------------------------------------------------------------------


	# Return the list of all the lists of stream points -----------------------
	# contained in the given reaches
	def getAllStreamFromReach(self,list_Reach):
		l_stream=[]
		for reach in list_Reach:
			l_stream.append(reach.getStreamList())
		return l_stream
	# -------------------------------------------------------------------------


	# Return a numpy array filled with zeros ----------------------------------
	def getNullFigure(self):
		a_Image = npy.zeros((self.river.row,self.river.col,3),npy.uint8)
		return a_Image
	# -------------------------------------------------------------------------


	# Draw the river contours -------------------------------------------------
	def drawRiverContour(self,a_Image,color):
		self.river.drawContours(a_Image,color)
		return a_Image
	# -------------------------------------------------------------------------


	# Draw the junctions and reaches ie. the skeleton -------------------------
	def drawSkeleton(self,a_Image,color1,color2):
		for junction in self.l_junctions:
			junction.draw(a_Image,color1)
		for reach in self.l_reaches:
			reach.draw(a_Image,color2)
		return
	# -------------------------------------------------------------------------


	# Draw the junctions ------------------------------------------------------
	def drawJunction(self,a_Image,color):
		for junction in self.l_junctions:
			junction.draw(a_Image,color)
		return
	# -------------------------------------------------------------------------


	# Draw green lines perpendicular to the stream points ---------------------
	def drawStream(self,a_Image,l_Stream,color):
		for list_temp in l_Stream:
			for stream in list_temp:
				stream.Draw(a_Image,color)
		return
	# -------------------------------------------------------------------------
	# -----------------------------------------------------------------------------------





	# Not Needed ------------------------------------------------------------------------
	"""
	def FilterBadReach(self,ReachThreshold):
		list_GoodReach=[]
		for i in range(len(self.l_reaches)):
			if (self.l_reaches[i].Distance<ReachThreshold) and (ReachThreshold>0): continue
			list_GoodReach.append(self.l_reaches[i])
		return list_GoodReach

	def getValues(self,list_stream):
		l_values=[]
		for list_temp in list_stream:
			l_temp=[]
			for stream in list_temp:
				l_temp.append((stream.width,stream.point[0],stream.point[1]))
			l_values.append(l_temp)
		return l_values

	def getWidth(self,list_stream):
		l_width = []
		for list_temp in list_stream:
			l_temp=[]
			for stream in list_temp:
				l_temp.append(stream.width)
			l_width.append(l_temp)
		return l_width

	def getAllStream(self):
		return self.getAllStreamFromReach(self.l_reaches)

	def FilterBadStreamWithHighWidth(self,l2_stream,highWidth):
		# we remove erroneous transect those which has extreme width
		l2_newStream=[]
		for list_stream in l2_stream:
			l_newStream=[]
			for stream in list_stream:
				if stream.width<highWidth:
					l_newStream.append(stream)
			if l_newStream:
				l2_newStream.append(l_newStream)
		return l2_newStream

	def FilterBadStreamFromMedian(self,list_Reach,WidthThreshold):
		l_stream=[]   
		for reach in list_Reach:
			list_temp = []
			if reach.ReachID == 0: continue
			for stream in reach.getStreamList():
				if stream.width>0 and (stream.width < float(WidthThreshold)*reach.MedianWidth): # we don't calculate width, if it is 2.5 time wider than the meadian width value
					list_temp.append(stream)
			l_stream.append(list_temp)
		return l_stream

	def FilterBadStreamFromMean(self,list_Reach,WidthThreshold):
		l_stream=[]   
		for reach in list_Reach:
			list_temp = []
			if reach.ReachID == 0: continue
			for stream in list_Reach.getStreamList():
				if stream.width>0 and (stream.width < float(WidthThreshold)*reach.avgWidth):
					list_temp.append(stream)
			l_stream.append(list_temp)
		return l_stream

	def FilterOnlyMedian(self,list_Reach):
		l_stream=[]
		for reach in list_Reach:
			if reach.ReachID==0: continue
			list_stream = reach.getStreamList()
			if len(list_stream)<1: continue
			list_temp=[]
			list_temp.append(list_stream[reach.MedianIndex])
			l_stream.append(list_temp)
		return l_stream

	def drawReach(self,a_Image,color):
		for reach in self.l_reaches:
			reach.draw(a_Image,color)
		return

	def drawReachFromList(self,a_Image,l_Reach,color):
		for reach in l_Reach:
			reach.draw(a_Image,color)
		return

	def drawImageWithStream(self,l_Stream):
		# call this function to print river contour, junction, skeleton and markings
		a_Image = npy.zeros((self.river.row,self.river.col,3),npy.uint8)
		self.river.drawContours(a_Image,rgbBLUE)

		for junction in self.l_junctions:
			junction.draw(a_Image,rgbCYAN)
		for reach in self.l_reaches:
			reach.draw(a_Image)
		self.drawStream(a_Image,l_Stream,rgbGREEN)
		return a_Image

	def drawReachWithPlot(self,l_Reach,plt,color):
		for reach in l_Reach:
			reach.drawWithPlot(plt,color)
		return

	def draw(self):
		a_Image = npy.zeros((self.river.row,self.river.col,3),npy.uint8)
		self.river.drawContours(a_Image,rgbBLUE)

		for junction in self.l_junctions:
			junction.draw(a_Image,rgbCYAN)
		for reach in self.l_reaches:
			reach.draw(a_Image)
		return a_Image

	def getDistance(self,list_Reach):
		l_dist=[]
		for reach in list_Reach:
			l_dist.append(reach.Distance)
		return l_dist

	def getAllStreamDistance(self,list_Reach):
		l_dist=[]
		for reach in list_Reach:
			l_dist.append(reach.getAllStreamDistance())
		return l_dist

	def getStreamDistanceFromList(self,list_stream):
		list_dist=[]
		for list_temp in list_stream:
			l_width=[]
			for stream in list_temp:
				l_width.append(stream.getDistanceFromStart())
			list_dist.append(l_width)
		return list_dist

	def checkPointInReachList(self,pos,list_Reach):
		for reach in list_Reach:
			for stream in reach.list_Stream:
				if (stream.point[0]==pos[0]) and (stream.point[1]==pos[1]):
					return True, stream
		return False,[]

	def checkPointInL2Stream(self,pos,l2_stream):
		for l_stream in l2_stream:
			for stream in l_stream:
				if (stream.point[0]==pos[0]) and (stream.point[1]==pos[1]):
					return True, stream
		return False,[]

	def findAvgWidthDischarge(self,l_Transect,threshold):
		# this calculate discharge for each thread, sum it and avereged it for given reach length
		sumWidth = 0
		sumDischarge = 0
		Count = 0
		InitRow = 0
		l_avgDetails = []
		for Transect in l_Transect:
			rowNumber = Transect.getRowNumber()
			if InitRow == 0:
				InitRow = rowNumber
			elif rowNumber-InitRow > threshold:
				l_avgDetails.append((Count,sumWidth/float(Count),sumDischarge/float(Count)))
				InitRow = rowNumber
				Count = 0
				sumDischarge = 0
				sumWidth = 0
			sumDischarge = sumDischarge + Transect.getDischarge()
			sumWidth = sumWidth + Transect.getWidth()
			Count = Count+1
		if (Count > 0):
			l_avgDetails.append((Count,sumWidth/float(Count),sumDischarge/float(Count)))
		return l_avgDetails

	def getStreamCumulativeDistance(self,l_Transect):
		l_listOfCumDistance = []
		dist=0
		flag=0
		prev=(0,0)
		# numt=0
		for Transect in l_Transect:
			# numt=numt+1
			# if numt>2: return l_listOfCumDistance
			if flag==0:
				prev=Transect.getMidReachValue()
				pos=prev
				flag=1
				l_listOfCumDistance.append((pos[0],pos[1],dist,Transect.getWidth(),Transect.getDischarge()))
				continue
			pos = Transect.getClosestMidReachValue(prev)
			# pos=Transect.getMidReachValue()
			if (pos[1]==0): continue
			dist = dist+npy.sqrt((pos[0]-prev[0])**2 + (pos[1]-prev[1])**2)
			l_listOfCumDistance.append((pos[0],pos[1],dist,Transect.getWidth(),Transect.getDischarge()))
			prev=pos
		return l_listOfCumDistance

	def getl2StreamFromlTransect(self,l_Transect):
		l2_Stream = []
		for Transect in l_Transect:
			l2_Stream.append(Transect.getlStream())
			
		return l2_Stream

	def findGoodTransect(self,list_goodReach,l2_stream):
		print ("Identifying good Transect")
		l_goodTransect=[]
		for i in range(self.skeleton.row):
			list_OfStream=[]
			bool_goodTransect=True
			sumWidth = 0
			sumDischarge = 0
			for j in range(self.skeleton.col):
				# print i,j
				# If you dont want to remove junction point, in the calculation then uncomment the next 2 statements and comment the following one
				if not self.skeleton.isSkeleton(i,j): continue
				bool_isInList1,stream = self.checkPointInL2Stream((i,j),l2_stream)
				bool_isInList2,stream = self.checkPointInReachList((i,j),list_goodReach)
				if (bool_isInList1 and bool_isInList2):
					list_OfStream.append(stream)
					sumWidth = stream.width + sumWidth
					sumDischarge = stream.Discharge + sumDischarge
				else:
					bool_goodTransect=False
			if bool_goodTransect and list_OfStream:
				transect = Transect(i,list_OfStream,sumWidth,sumDischarge)
				l_goodTransect.append(transect)
		return l_goodTransect

	def printL2Stream(self,l2_stream):
		for l_stream in l2_stream:
			for stream in l_stream:
				stream.printInfo()
		return
	"""
# End of class ------------------------------------------------------------------------------------
