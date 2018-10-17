# Modules to import -------------------------------------------------------------------------------
import numpy as npy
from skimage import morphology
from matplotlib import pyplot as plt
from river import River
from stream import Stream
from reach import Reach
from junction import Junction
# -------------------------------------------------------------------------------------------------

# Global Variables --------------------------------------------------------------------------------
flag_BLACK=0
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

# Class - Skeleton --------------------------------------------------------------------------------
class Skeleton:
	# Class variables -------------------------------------------------------------------
	array_skeleton=[] # array to contain the river skeleton
	row=0 # number of rows of the skeleton array
	col=0 # number of columns of the skeleton array
	length_dangling_arcs=0 # allowed length of the dangling arcs
	array_Junction=[] # array to mark junction points and its neighbourhood points with unique IDs
	array_done=[] # array to mark junction points, its neighbourhood area points with their corresponding junction-IDs and stream points with their reach-IDs
	list_Junction=[] # list to store all Junction type variables
	l_Reach=[] # list to store all Reach type variables
	flag_fast=0 # if flag_fast is set to 1, then the class performs only fast functions
	# -----------------------------------------------------------------------------------

	# Constructor function --------------------------------------------------------------
	def __init__(self,river,len_dang_arcs,fast):
		# Initialize the variables
		self.array_skeleton=[]
		self.row=0
		self.col=0
		self.length_dangling_arcs=len_dang_arcs
		self.array_Junction=[]
		self.array_done=[]
		self.list_Junction=[]
		self.l_Reach=[]
		self.flag_fast=fast

		# Find the skeleton and extract the river boundary
		# By the end of this constructor function we have a skeleton of the river with no dangling arcs, with junction points and reaches identified

		# 1. Get the river image in the form of numpy array -------------------
		array_Image = river.getRiver()

		# 2. Find skeleton for the river --------------------------------------
		print ("Finding the skeleton")
		self.array_skeleton = morphology.skeletonize(array_Image>0)
		self.array_skeleton = npy.array(self.array_skeleton,dtype=npy.uint8)
		(self.row,self.col) = self.array_skeleton.shape
		# ---------------------------------------------------------------------
		# image after taking the skeleton of river
		plt.imshow(self.array_skeleton)
		plt.savefig('temp/10_Skeleton.png', format = 'jpg', dpi=1200)
		# ---------------------------------------------------------------------

		# 3. Remove dangling arcs ---------------------------------------------
		if not fast:
			print ("Removing dangling arcs")
			self.RemoveDanglingArc()
			# -----------------------------------------------------------------
			# image after removing dangling arcs form the skeleton
			plt.imshow(self.array_skeleton)
			plt.savefig('temp/11_RemoveDanglingArc.png', format = 'jpg', dpi=1200)
			# -----------------------------------------------------------------

		# 4. Find the junction points -----------------------------------------
		print ("Identifying all the junctions")
		self.array_done = npy.zeros((self.row,self.col), dtype=npy.int)
		self.array_Junction = npy.zeros((self.row,self.col), dtype=npy.int)
		self.MarkJunctions()
		# ---------------------------------------------------------------------
		# image after finding the junctions of the river
		plt.imshow(self.array_Junction)
		plt.savefig('temp/12_Junctions.png', format = 'jpg', dpi=1200)
		# ---------------------------------------------------------------------

		# 5. Identify all the reaches -----------------------------------------
		print ("Identifying all the reaches")
		reach = Reach(0) # create a new Reach type variable with ReachID = 0
		self.l_Reach.append(reach) # append it to the list - l_Reach
		self.IdentifyReach()

		# self.MarkJunctionsAndNeighbourhood()
		# self.MarryReachJunction()
		return
	# -----------------------------------------------------------------------------------


	# Class Functions -------------------------------------------------------------------
	# Run TraverseDanglingArc() on all next points of each junction -----------
	def RemoveDanglingArc(self):
		for i in range(self.row):
			for j in range(self.col): # for each point (i,j)
				bool_isJunc,list_nextPoints = self.isJunctionAndNextPoint(i,j,0) # check if it is a juction point
				if bool_isJunc: # if it is a junction point
					for (x,y) in list_nextPoints: # run TraverseDanglingArc() function on all of its next points 
						self.TraverseDanglingArc(x,y,i,j,0)
		return
	# -------------------------------------------------------------------------


	# Check if the given point is a junction and find its next points ---------
	def isJunctionAndNextPoint(self,x,y,to_return):
		cur=(x,y)
		list_nextPoints=[] # to store the points next to the junction point
		nextP=[] # to store the 4 points surrounding a junction point
		nextP.append([cur[0],cur[1]-1])
		nextP.append([cur[0],cur[1]+1])
		nextP.append([cur[0]-1,cur[1]])
		nextP.append([cur[0]+1,cur[1]])
		flag=[False for _ in range(4)]
			
		for j in range(len(nextP)):
			# find all the neighbouring points that belong to the skeleton
			# append them to the list - list_nextPoints
			pos = nextP[j]
			if pos[0]<0 or pos[0]>=self.row or pos[1]<0 or pos[1]>=self.col: continue
			if not self.isSkeleton(pos[0],pos[1]): continue
			list_nextPoints.append(pos)
			flag[j]=True
				
		# now find all the neighbouring diagonal points that belong to the skeleton
		# append them to the list - list_nextPoints
		if flag[0]==False and flag[2]==False and self.isSkeleton(cur[0]-1,cur[1]-1):
			list_nextPoints.append([cur[0]-1,cur[1]-1])
		if flag[0]==False and flag[3]==False and self.isSkeleton(cur[0]+1,cur[1]-1):
			list_nextPoints.append([cur[0]+1,cur[1]-1])
		if flag[1]==False and flag[2]==False and self.isSkeleton(cur[0]-1,cur[1]+1):
			list_nextPoints.append([cur[0]-1,cur[1]+1])
		if flag[1]==False and flag[3]==False and self.isSkeleton(cur[0]+1,cur[1]+1):
			list_nextPoints.append([cur[0]+1,cur[1]+1])

		# 0 - to return junction-check result as well as the next points
		if to_return == 0:
			if (len(list_nextPoints)>2): return 1, list_nextPoints
			else: return 0, list_nextPoints
		# -1 - to return junction-check result
		elif to_return == -1:
			if (len(list_nextPoints)>2): return 1
			else: return 0
	# -------------------------------------------------------------------------


	# Traverse the arc to find if its a dangling arc --------------------------
	# we delete the small segments of skeleton which is less than self.length_dangling_arcs number of pixels
	def TraverseDanglingArc(self,i,j,prevI,prevJ,noOfPixel):
		# if length of the arc is greater than self.length_dangling_arcs, do nothing
		if noOfPixel>self.length_dangling_arcs:
			return 0
		# if we reach a junction, do nothing
		bool_isJunc,list_nextPoints=self.isJunctionAndNextPoint(i,j,0)
		if bool_isJunc:
			return 0

		# recursively run the TraverseDanglingArc() function on the next points
		deletePath=0
		for (x,y) in list_nextPoints:
			if (x==prevI) and (y==prevJ): continue # do not traverse the arc in the reverse direction
			deletePath=self.TraverseDanglingArc(x,y,i,j,noOfPixel+1) # recurse the function on the adjacent points
			if (deletePath):
				self.array_skeleton[i][j]=flag_BLACK # delete the point (i,j) - paint it black
			return deletePath
		self.array_skeleton[i][j]=flag_BLACK # if end of the arc is reached then delete the whole arc
		return 1
	# -------------------------------------------------------------------------


	# Run addToJunction() on all junction points ------------------------------
	def MarkJunctions(self):
		self.addToJunction([0,0]) # initially run addToJunction() on the point (0,0)
		flag=True
		for i in range(self.row): # for each point (i,j)
			for j in range(self.col):
				# the first skeleton point is always considered as a junction
				# important for images with no junction points
				if self.isSkeleton(i,j) and flag:
					self.addToJunction([i,j])
					flag = False
				# check if the point is a junction point
				elif self.isJunctionAndNextPoint(i,j,-1):
					self.addToJunction([i,j]) # if it is, run addToJunction() on it
		return
	# -------------------------------------------------------------------------


	# Create Junction type variables with unique junction-IDs -----------------
	# and find the junction neighbourhood
	def addToJunction(self,pos):
		x=pos[0]
		y=pos[1]
		junctionID=self.array_Junction[x][y] # get the junction-ID of that point

		# if no junction-ID is alloted up till now
		if not junctionID:
			junctionID=len(self.list_Junction) # get a new junction ID
			junction=Junction(pos,junctionID) # create a new Junction type variable with that ID
			self.list_Junction.append(junction) # append this Junction variable to the list - list_Junction

		# find the neighbours of that junction point in some given area
		for i in range(-2,3): 
			for j in range (-2,3):
				if (x+i<0) or (y+j < 0) or (x+i > self.row) or (y+j> self.col): continue
				if self.isSkeleton(x+i,y+j): # if the neighbour is part of the skeleton
					self.array_Junction[x+i][y+j]=junctionID # give it the same junction-ID
					self.list_Junction[junctionID].addJunctionNeighbourhood([x+i,y+j]) # append its position to the list - list_junctionArea
					self.array_done[x+i][y+j]=1 # mark that neighbourhood point as done
		return
	# -------------------------------------------------------------------------


	# Check if a point is part of the skeleton --------------------------------
	def isSkeleton(self,x,y):
		if (x>=self.row) or (y>=self.col): return 0
		if self.array_skeleton[x][y]: return 1
		return 0
	# -------------------------------------------------------------------------


	# Run TraverseReach() on all junction points ------------------------------
	def IdentifyReach(self):
		for junc in self.list_Junction: # for each Junction type variable
			if junc.JunctionID==0: continue # if junction-ID == 0, skip

			for pos in junc.list_junctionArea: # for its and each of its neighbour's positions
				l_nextPoints=self.getNextPoints(pos) # get the list of next points emerging from a point of that junction neighbourhood

				if (len(l_nextPoints)==1): # if only one such point is found
					start=l_nextPoints[0] # put the position of that point into start
					end,reach=self.TraverseReach(start) # run TraverseReach() on that point
					endJunc=self.list_Junction[self.array_Junction[end[0],end[1]]] # find junction for that end point
					self.addReachToJunction(reach,junc,endJunc) # Run the function - addReachToJunction(), on the current reach, the start junction and the end junction
		return
	# -------------------------------------------------------------------------


	# Traverse a reach staring from the point cur -----------------------------
	def TraverseReach(self,cur):
		reachID=len(self.l_Reach) # get a new reach-ID
		reach=Reach(reachID) # create a new Reach type variable with that ID
		
		self.array_done[cur[0],cur[1]]=reachID # mark array done for that first non-junction skeleton point by its reach-ID
		list_nextPoints=self.getNextPoints(cur) # calculate the next non-junction skeleton point
		while (len(list_nextPoints)==1): # if only one such point exists
			cur=list_nextPoints[0]
			reach.addToStream(cur) # Run addToStream() on that point
			self.array_done[cur[0],cur[1]]=reachID # give this new point the same reach-ID a its previous point
			list_nextPoints=self.getNextPoints(cur) # proceed to the next point

		self.l_Reach.append(reach) # append this new reach ending with the point - cur, to the list - l_Reach
		return cur, reach
	# -------------------------------------------------------------------------


	# Store data of the current reach into its start and end junctions --------
	# And also start and end junction information in the reach
	def addReachToJunction(self,reach,juncStart,juncEnd):
		juncStart.addReach(reach) # store the current reach in the starting junction
		juncEnd.addReach(reach) # store the current reach in the ending junction
		reach.addJunction(juncStart) # store info of the start junction in the current reach
		reach.addJunction(juncEnd) # store info of the end junction in the current reach
		return
	# -------------------------------------------------------------------------


	# Find and return the next points to a junction neighbourhood area --------
	def getNextPoints(self,cur):
		list_nextPoints=[] # to store the points next to the junction neighbourhood area
		nextP=[] # to store the 4 points surrounding a junction neighbourhood point
		nextP.append([cur[0],cur[1]-1])
		nextP.append([cur[0],cur[1]+1])
		nextP.append([cur[0]-1,cur[1]])
		nextP.append([cur[0]+1,cur[1]])
		flag=[False for _ in range(4)]

		for j in range(len(nextP)):
			pos = nextP[j]
			if pos[0]<0 or pos[0]>=self.row or pos[1]<0 or pos[1]>=self.col: continue
			# if the point is already marked in array_done, set flag = True but do not add it into the list - list_nextPoints
			if self.array_done[pos[0]][pos[1]]:
				flag[j]=True
				continue
			# if the point is not a part of the skeleton, then skip
			if not self.isSkeleton(pos[0],pos[1]): continue
			# find all the neighbouring points that belong to the skeleton and are unmarked in the array_done
			# append them to the list - list_nextPoints
			list_nextPoints.append(pos)
			flag[j]=True

		# now find all the neighbouring diagonal points that belong to the skeleton and are unmarked in the array_done
		# append them to the list - list_nextPoints
		if flag[0]==False and flag[2]==False and self.isSkeleton(cur[0]-1,cur[1]-1) and not self.array_done[cur[0]-1][cur[1]-1]:
			list_nextPoints.append([cur[0]-1,cur[1]-1])
		if flag[0]==False and flag[3]==False and self.isSkeleton(cur[0]+1,cur[1]-1) and not self.array_done[cur[0]+1][cur[1]-1]:
			list_nextPoints.append([cur[0]+1,cur[1]-1])
		if flag[1]==False and flag[2]==False and self.isSkeleton(cur[0]-1,cur[1]+1) and not self.array_done[cur[0]-1][cur[1]+1]:
			list_nextPoints.append([cur[0]-1,cur[1]+1])
		if flag[1]==False and flag[3]==False and self.isSkeleton(cur[0]+1,cur[1]+1) and not self.array_done[cur[0]+1][cur[1]+1]:
			list_nextPoints.append([cur[0]+1,cur[1]+1])
		return list_nextPoints
	# -------------------------------------------------------------------------
	# -----------------------------------------------------------------------------------





	# Not Needed ------------------------------------------------------------------------
	"""
	def draw(self,a_Image,color):
		for i in range(self.row):
			for j in range(self.col):
				if self.isJunctionAndNextPoint(i,j,-1):
					a_Image[i][j]=rgbRED
				elif self.isSkeleton(i,j):
					a_Image[i][j]=color
		return

	def printAround(self,i,j):
		for x in range(-2,3):
			str = ''
			for y in range(-2,3):
				str = str + "%s " % self.array_skeleton[i+x][j+y]
			print (str)
		return

	def isNeighbour(self,neigh1,neigh2):
		if abs(neigh1[0]-neigh2[0]) > 1: return False
		if abs(neigh1[1]-neigh2[1]) > 1: return False
		return True

	'''
	def MarkJunctionsAndNeighbourhood(self):
		print "Ya. Inside latest attempt :)"
		#Create dummy reach and Junction. This is to ensure that reachID and junctionID will always be >0
		self.addToJunction([0,0])
		reach = Reach(0)
		self.l_Reach.append(reach)
		l_junc=[]
		self.array_done = npy.zeros((self.row,self.col), dtype=npy.int)
		for i in range(self.row):
			for j in range(self.col):
				if self.isSkeleton(i,j):
					l_junc.append([i,j])
					self.addToJunction([i,j])
					while l_junc:
						nextP=l_junc.pop(0)
						if self.array_done[nextP[0]][nextP[1]]: continue
						list_nextPoints = self.loop_TraverseReach(nextP)
						l_junc.extend(list_nextPoints)
					return

	def loop_TraverseReach(self,cur):
		reachID=len(self.l_Reach)
		reach = Reach(reachID)
		self.array_done[cur[0],cur[1]]=reachID
		list_nextPoints = self.getNextPoints(cur)
		while (len(list_nextPoints) == 1):
			cur = list_nextPoints[0]
			reach.addToStream(cur)
			self.array_done[cur[0],cur[1]]=reachID
			list_nextPoints = self.getNextPoints(cur)
		self.l_Reach.append(reach)
		if (len(list_nextPoints)>1):
			self.addToJunction(cur)
		return list_nextPoints

	def MarryReachJunction(self):
		print "Identifying the Reache's junctions and vice versa"
		# for reach in self.l_Reach:
		# 	if reach.ReachID == 0: continue
		for junction in self.list_Junction:
				# if junction.position[0] == 0: continue
			for pos in junction.list_junctionArea:
				reachid = self.array_done[pos[0]][pos[1]]
				if reachid > 0:
					reach = self.l_Reach[reachid]
					# if pos==reach.start or pos==reach.end:
					junction.addReach(reach)
					reach.addJunction(junction)
	'''

	def Draw(self,i):
		plt.figure(i)
		plt.imshow(self.array_skeleton)
		return

	def MergeWithRiver(self,river):
		newImg = npy.zeros((self.row,self.col,3),npy.uint8)
		newImg.fill(255)
		for i in range(self.row):
			for j in range(self.col):
				if self.array_Junction[i][j]:
					newImg[i][j]=rgbRED
				elif self.array_done[i][j]:
					newImg[i][j]=rgbWHITE
				elif river.isRiver(i,j):
					newImg[i][j] = rgbBLUE
		return newImg
	"""
# End of class ------------------------------------------------------------------------------------
