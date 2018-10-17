# Modules to import -------------------------------------------------------------------------------
from reach import Reach
# -------------------------------------------------------------------------------------------------

# Global Variables --------------------------------------------------------------------------------
rgbRED=[255.0,0.0,0.0]
rgbYELLOW=[255.0,255.0,0.0]
# -------------------------------------------------------------------------------------------------

# Class - Junction --------------------------------------------------------------------------------
class Junction:
	# Class variables -------------------------------------------------------------------
	JunctionID=0 # unquie ID for each Junction type variable
	position=[0,0] # position of the point
	list_junctionArea=[] # store positions of its neighbouring points
	l_Reach=[] # store the reaches connected to that junction
	# list_NeighbourReach=[]
	# -----------------------------------------------------------------------------------

	# Constructor function --------------------------------------------------------------
	def __init__(self,pos,jid):
		# Initialize the variables
		self.JunctionID=jid
		self.position=pos
		self.list_junctionArea=[]
		self.l_Reach=[]
		return
	# -----------------------------------------------------------------------------------


	# Class Functions -------------------------------------------------------------------
	# Store positions of neighbouring points ----------------------------------
	def addJunctionNeighbourhood(self,pos):
		self.list_junctionArea.append(pos)
		return
	# -------------------------------------------------------------------------


	# Store the reach variable to which the given junction is connected -------
	def addReach(self,reach):
		self.l_Reach.append(reach)
		return
	# -------------------------------------------------------------------------


	# Draw the junction areas -------------------------------------------------
	def draw(self,a_Image,rgb_color):
		for pos in self.list_junctionArea:
			a_Image[pos[0]][pos[1]]=rgb_color
		return
	# -------------------------------------------------------------------------
	# -----------------------------------------------------------------------------------





	# Not Needed ------------------------------------------------------------------------
	"""
	def addToNeighbours(self,pos,neighbour, reach):
		self.list_NeighbourReach.append([pos,neighbour,reach])
		return

	def getJunction(self):
		return self.junction

	def getJunctionPosition(self):
		if not self.junction:
			return self.junction.location
		else:
			return (0,0)

	def getInBetweenReach(self,junction):
		pos1 = junction.getJunctionPosition()
		for a in self.list_NeighbourReach:
			print("a")
			neighbour=a[1]
			pos2 = neighbour.getJunctionPosition()
			if(pos1[0] == pos2[0]) and (pos1[1] == pos2[1]):
				return a[2]
		return 0

	def mergeWithFigure(self,array_Image):
		junc = self.junction
		(x,y) = junc.location
		print ("Junction = (",x,y,junc.JunctionID,")")
		array_Image[x][y] = rgbRED
		for l in junc.list_Branches:
			(i,j) = l
			array_Image[i][j]=rgbYELLOW

		for a in self.list_NeighbourReach:
			print ("Going to Neighbour")
			a[2].drawGreen(array_Image)
			a[1].mergeWithFigure(array_Image)
		return
	"""
# End of class ------------------------------------------------------------------------------------
