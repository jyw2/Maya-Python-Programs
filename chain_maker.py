from maya import cmds
import math

class Window:
	"""Creates a window and an associated chain obj. Takes no arguments"""

	def __init__(self):
			
		self.windowName = "Chain_Maker"

		#if window already exists close it first
		if cmds.window(self.windowName, ex = True):
			self.cancel()

		#Initiate chain and window
		self.chain = Chain(1)
		self.links = 1
		self.radius = 0.5
		self.radiusLink = 0.05
		cmds.window(self.windowName,iconName = "Chain Maker")
		
		#build UI
		col = cmds.columnLayout(adjustableColumn = True, co = ("both",100),rs = 10)

		cmds.text("Number of Links",h=30 )
		cmds.rowLayout(nc = 2,ad2 = 2,cw = (1,30))
		self.linkText = cmds.text(label = "1")
		self.linksSlider = cmds.intSlider(min = 1, max = 100, value = 1, dc = self.mod_links)
		cmds.setParent(col)


		cmds.text("Radius of Links")
		self.radiusSlider = cmds.floatSlider(min = 0.15, max = 2, value = 0.5 , dc = self.mod_radius)

		cmds.text("Radius of Thickness of Links")
		self.thicknessSlider = cmds.floatSlider(min = 0.01, max = 0.5, value = 0.05 , dc = self.mod_thickness)


		
		cmds.button("Confirm", c =self.confirm)

		cmds.button("Cancel", c = self.cancel)

		cmds.showWindow()

	def mod_links(self,*args):
		"""modifies the link in an existing chain. Note that the chain
		is REPLACED with each call.Takes no arguments other than self"""
		self.links = cmds.intSlider(self.linksSlider, q = True, v = True)
		if self.links > 1:
			self.recreate_chain()
			cmds.text(self.linkText,edit=True, label = str(self.links))

	
	def mod_radius(self,*args):
		"""Modifies the radius of an existing chain. Note that the chain
		is REPLACED with each call.Takes no arguments other than self"""
		#Create new chain and modify thickness slider to prevent clipping
		self.radius = cmds.floatSlider(self.radiusSlider, q = True, v = True)
		self.recreate_chain()
		cmds.floatSlider(self.thicknessSlider, e = True, max = self.radius/3)

	
	def mod_thickness(self,*args):
		"""modifies the thickness of an existing chain. Note that the chain
		is REPLACED with each call.Takes no arguments other than self"""
		#Create new chain and modify rad slider to prevent clipping
		self.radiusLink = cmds.floatSlider(self.thicknessSlider, q = True, v = True)
		print self.radiusLink
		self.recreate_chain()
		cmds.floatSlider(self.radiusSlider, e = True, min= self.radiusLink*3)

	def recreate_chain(self):
		"""Deletes old chain and creates a new chain based on new parameters.Takes no arguments other than self"""
		cmds.delete(self.chain.delete_chain())
		chain = Chain(self.links, radius= self.radius, linkRadius= self.radiusLink)

	def confirm(self,*args):
		"""Closes the UI without affecting the chain.Takes no arguments other than self"""
		cmds.deleteUI(self.windowName)



	def cancel(self,*args):
		"""Closes UI and deletes chain.Takes no arguments other than self"""
		cmds.deleteUI(self.windowName)
		cmds.delete(self.chain.delete_chain())



class Ring():
	"""A ring in the chain. Stores it's transform string,node string and place on the chain.
	Arguments:
		ringNumber: number of links or rings, radius: radius of the rings, linkRadius: radius of the thickness"""
	def __init__(self,ringNumber,radius,linkRadius):

		#diffirent naming for the first ring
		if ringNumber == 0:
			(self.transform,self.shape) = cmds.polyTorus(r=radius,sr=linkRadius, name = "Chain_root")
			self.ringName = self.transform

		#Naming for all other rings. 
		else:
			(self.transform,self.shape) = cmds.polyTorus(r=radius,sr=linkRadius, name = "ring_"+str(ringNumber))
			self.ringName = self.transform

		self.ringNumber = ringNumber
		
	def add_parent(self,parentName):
		"""updates the ring transform id after being parented"""
		self.transform = parentName+"|"+self.transform	

	def get_transform(self):
		return self.transform
	def get_shape(self):
		return self.shape
	def get_ringNumber(self):
		return self.ringNumber
	def get_name(self):
		return self.ringName

	def delete_link(self):
		"""Removes itself"""
		cmds.delete(self.transform)

		
			

class Chain():
	"""Creates a chain of rings. The first ring is treated as the root
	ring. 
	
		Attributes:
			links = number of links
			radius = radius of links
			linkRadius = thickness of each link	
	"""
	
	def __init__(self,links,radius = 0.5,linkRadius=0.05):
		self.links = links
		self.radius = radius
		self.linkRadius = linkRadius
		self.linkObjs = []
		self.rotationState = False
		self.linkNumber = 0

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
		cmds.setAttr(ring.get_shape() + ".subdivisionsAxis", 4)# change subdivisions to get rectangular shape
		cmds.setAttr(ring.get_transform() + ".rotateY",45) # rotation in xz plane
		
		cmds.polySelect(ring.get_transform(), el = 100) # stretching the square
		cmds.polySelect(ring.get_transform(), el = 85,add = True)
		cmds.polyMoveEdge(translateX = (float(-self.radius)*(2.0-math.sqrt(2))/2))

		cmds.polySelect(ring.get_transform(), el = 90)# stretching the square at opposite corners
		cmds.polySelect(ring.get_transform(), el = 95, add = True)
		cmds.polyMoveEdge(translateX =(float( self.radius)*(2.0-math.sqrt(2))/2))

		#rotate along chain axis every 2nd link
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

		#Create links
		for link in range(self.links):
			self.create_link()

		#parent all links to the first
		for link in range(1,len(self.linkObjs)):
			cmds.parent((self.linkObjs[link]).get_name(),self.linkObjs[0].get_name())
			self.linkObjs[link].add_parent(self.linkObjs[0].get_transform())


	def delete_chain(self):
		"""Removes the chain"""
		rootname = self.linkObjs[0].get_transform()
		cmds.delete(rootname)

#initiates the program
window = Window()



	