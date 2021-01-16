from maya import cmds
import math



class Window:
	"""Creates a window"""
	def __init__(self):
			
		self.windowName = "chainWindow"

		#if window already exists
		if cmds.window(self.windowName, ex = True):
			self.cancel()

		cmds.window(self.windowName,iconName = "Chain Maker")
		
		#build UI
		cmds.columnLayout(adjustableColumn = True, co = ("both",100))
		cmds.intSlider("Links", min = 1, max = 100, value = 1)
		cmds.button("Confirm", c =self.confirm)
		cmds.button("Cancel", c = self.cancel)

		cmds.showWindow()


	def confirm(self,*args):
		cmds.deleteUI(self.windowName)



	def cancel(self,*args):
		cmds.deleteUI(self.windowName)


	









class Ring():
	"""A ring in the chain. Stores it's transform string,node string and place on the chain"""
	def __init__(self,ringNumber,radius,linkRadius):

		#diffirent naming for the first ring
		if ringNumber == 0:
			(self.transform,self.shape) = cmds.polyTorus(r=radius,sr=linkRadius, name = "Chain_root")
			self.ringName = self.transform

			# change pivot to allow easier whole chain scaling
			# cmds.setAttr(self.transform,ax)

		#Naming for all other rings. Also parents the rings to the first ring.
		else:
			(self.transform,self.shape) = cmds.polyTorus(r=radius,sr=linkRadius, name = "ring_"+str(ringNumber))
			self.ringName = self.transform
			


		self.ringNumber = ringNumber
		
	def get_transform(self):
		return self.transform
	def get_shape(self):
		return self.shape
	def get_ringNumber(self):
		return self.ringNumber
	def get_name(self):
		return self.ringName

		
			

class Chain():
	"""Creates a chain of rings. The first ring is treated as the root
	ring. 
	
		Attributes:
			links = number of links
			radius = radius of links
			linkRadius = thickness of each link	
	"""
	
	def __init__(self,links,radius = 0.5,linkRadius=0.05,squish =0.75 ):
		self.links = links
		self.radius = radius
		self.linkRadius = linkRadius
		self.linkObjs = []
		self.rotationState = False
		self.linkNumber = 0
		self.scale = squish



		#ensure the links will fit in the hole without clipping
		if not (4*self.linkRadius<= self.radius):
			raise ValueError("Rings are too fat and or short, try reducing link radius or increasing radius")

		self.create_chain()

	def move_link(self,ring):
		"""Translate the ring based on its position in the chain."""
		magnitudeOfTranslate = (ring.get_ringNumber())*(self.radius)+(ring.get_ringNumber())*(self.radius-2*(self.linkRadius))
		cmds.move(magnitudeOfTranslate, 0, 0 , ring.get_transform())

	def create_link(self):
		"""Creates a ring
			
			Attributes:	
				linkNumber: What number of ring it is(the first is 0,
				second is 1 ... ETC)

			Returns:
				Ring object
		
		"""

		#general transforms
		ring = Ring(self.linkNumber,self.radius,self.linkRadius)
		cmds.setAttr(ring.get_shape() + ".subdivisionsAxis", 4)
		cmds.setAttr(ring.get_transform() + ".rotateY",45) # rotation in xz plane
		
		cmds.polySelect(ring.get_transform(), el = 100) # stretching the square
		cmds.polySelect(ring.get_transform(), el = 85,add = True)
		cmds.polyMoveEdge(translateX = 0.8*(float(-self.radius)*(2.0-math.sqrt(2))/2))

		cmds.polySelect(ring.get_transform(), el = 90)
		cmds.polySelect(ring.get_transform(), el = 95, add = True)
		cmds.polyMoveEdge(translateX =0.8*(float( self.radius)*(2.0-math.sqrt(2))/2))

	
		

		print "ringmade"
		if self.rotationState == True:
			cmds.rotate(90 ,0, 45, ring.get_transform(),ws=True)
			
		#Makes the next ring rotate 90 deg
		self.rotationState = not self.rotationState
		self.linkNumber += 1
		
		#stores the ring for later modifications
		self.linkObjs.append(ring)
		self.move_link(ring)
		return ring



		
	def create_chain(self):
		"""Creates and links in relationship all rings. The first
		ring is the root(parent)"""

		for link in range(self.links):
			self.create_link()

		for link in range(1,len(self.linkObjs)):
			print (self.linkObjs[link]).get_name()
			cmds.parent((self.linkObjs[link]).get_name(),self.linkObjs[0].get_name())
		

			
		


#Tests
#chain = Chain(20,radius=0.1, linkRadius=0.015)
window = Window()



	