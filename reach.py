# Modules to import -------------------------------------------------------------------------------
import numpy as npy
import random as random
from river import River
from stream import Stream
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

# Class - Reach -----------------------------------------------------------------------------------
class Reach:
	# Class variables -------------------------------------------------------------------
	ReachID=0 # unique ID for every Reach type variable
	start=(0,0) # starting point of the reach
	end=(0,0) # ending point of the reach
	list_Stream=[] # list of stream points contained inside the reach
	list_junction=[] # list of junctions that contain the reach
	Distance=0 # distance of the reach from the start point to the end point
	avgWidth=0 # average width of the reach
	MedianWidth=0 # median width of the reach
	MedianIndex=0 # index of the stream point in the list - list_Stream, which has the median width across it
	isGood=0 # not needed
	# -----------------------------------------------------------------------------------

	# Constructor function --------------------------------------------------------------
	def __init__(self,reachid):
		# Initialize the variables
		self.ReachID = reachid
		self.start=(0,0)
		self.end=(0,0)
		self.list_Stream=[]
		self.list_junction=[]
		self.Distance=0
		self.avgWidth=-1
		self.MedianWidth=0
		self.MedianIndex=0
		self.isGood=0
		return
	# -----------------------------------------------------------------------------------


	# Class Functions -------------------------------------------------------------------
	# Add stream points to a particular reach variable ------------------------
	def addToStream(self,point):
		if self.start == (0,0):
			# if it is the second point of that reach - set start equal to that point
			# NOTE - first point is just marked in the array - array_done
			self.start = point
		stream = Stream(point) # create a new Stream type variable for this point
		self.list_Stream.append(stream) # add this Stream type variable to the list - list_Stream of the current reach
		self.end=point # mark the latest point as the end point
		return
	# -------------------------------------------------------------------------


	# Store the start and end junctions for a given reach variable ------------
	def addJunction(self,pos):
		# if the list of junctions is already filled by the start and end junctions
		if len(self.list_junction)==2: return
		# if the list of junctions is empty, fill it
		if not self.list_junction: self.list_junction.append(pos)
		# if the list of junctions has one element, check before inserting to avoid duplicates
		elif (self.list_junction[0]!=pos): self.list_junction.append(pos)
		# declare error if more than two junctions for a single reach
		if (len(self.list_junction)>2):
			print ("Grave Error: ReachID=", self.ReachID, ", JunctionID=",pos.JunctionID, ", Position=",pos.position, ", length=",len(self.list_junction))
			print ("Start=",self.start, ", End=",self.end)
		return
	# -------------------------------------------------------------------------


	# Compute the distance of each stream point form the starting point -------
	# here starting point refers to the starting point of the reach
	def computeDistance(self):
		# if reach-ID == 0, do nothing
		if self.ReachID==0: return

		prev=self.start # store the starting point of the given reach into prev
		for stream in self.list_Stream: # for each stream point in the given Reach
			pos=stream.getLocation() # get the position of the current stream point
			self.Distance = npy.sqrt((pos[0]-prev[0])**2 + (pos[1]-prev[1])**2) + self.Distance # find the distance of the current stream point from the previous stream point, and add it to the total distance variable - Distance 
			prev=pos # update the previous stream point
			stream.setDistanceFromStart(self.Distance) # set the distance of the current stream point from the starting point of the reach
		return
	# -------------------------------------------------------------------------


	# Return the list of stream points in the given reach ---------------------
	def getStreamList(self):
		return self.list_Stream
	# -------------------------------------------------------------------------


	# Compute the average and median width for the given reach ----------------
	def ComputeAvgMean(self):
		# if reach-ID == 0, do nothing
		if self.ReachID==0: return
		# if the reach has no stream points, do nothing
		if len(self.list_Stream)<1: return

		l_width = []
		sumWidth = 0
		counter = 0
		for stream in self.list_Stream: # for each stream point
			if stream.width==-1: continue # if the width at this stream point was not calculated, skip this point

			sumWidth+=stream.width # take summation of widths across all the stream points left
			l_width.append(stream.width) # store each width value into the list - l_width
			counter+=1 # increment the counter

		# if none of the stream points had their widths calculated, do not calculate average width for this reach
		if counter==0: return

		self.avgWidth = sumWidth/counter # calculate the average width
		sorts = sorted(l_width) # sort the width list
		self.MedianWidth=sorts[counter//2] # find the median width
		for j in range(len(self.list_Stream)): # for each stream point
			if self.list_Stream[j].width==self.MedianWidth: # if the width across that stream point is equal to the median width
				self.MedianIndex=j # store the index of that stream point which has the median width
				break
		return
	# -------------------------------------------------------------------------


	# Draw the reaches --------------------------------------------------------
	def draw(self,a_Image,color):
		if self.ReachID == 0: return
		for j in range(len(self.list_Stream)):
			pos = self.list_Stream[j].getLocation()
			a_Image[pos[0]][pos[1]]=color
		return
	# -------------------------------------------------------------------------
	# -----------------------------------------------------------------------------------





	# Not Needed ------------------------------------------------------------------------
	"""
	def drawWithPlot(self,plt,pcolor):
		if len(self.list_Stream)<1: return
		stream = self.list_Stream[self.MedianIndex]
		toPrint = "d="+str(int(self.Distance))+",$\sigma$="+str(int(self.MedianWidth))
		plt.text(stream.point[1]+5,stream.point[0],toPrint,color=pcolor)
		# plt.text(10,100,toPrint)
		return

	def drawStream(self,a_Image,color):
		# print "Going to enter stream"
		for stream in self.list_Stream:
			stream.Draw(a_Image,color)
		return

	def getDistance(self):
		return Distance

	def getRandomStream(self):
		return self.list_Stream[random.randint(0,len(self.list_Stream)-1)]

	def getAllStreamDistance(self):
		l_dist = []
		for stream in self.list_Stream:
			l_dist.append(stream.getDistanceFromStart())
		return l_dist

	def getAllStreamWidth(self):
		l_dist = []
		for stream in self.list_Stream:
			l_dist.append(stream.getWidth())
		return l_dist

	def drawGreen(self,array_Image):
		print ("Inside Stream")
		for j in self.list_Stream:
			(x,y) = j.point
			array_Image[x][y]=rgbSAFFRON
			print (x,y)
		print ("Outside Stream")
		return
	"""
# End of class ------------------------------------------------------------------------------------
