from maya import cmds
import math



class Window:
	"""Creates a window"""
	def __init__(self):
			
		self.windowName = "Chain_Maker"

		#if window already exists
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
		self.links = cmds.intSlider(self.linksSlider, q = True, v = True)
		if self.links > 1:
			cmds.delete(self.chain.delete_chain())
			chain = Chain(self.links, radius= self.radius, linkRadius= self.radiusLink)
			cmds.text(self.linkText,edit=True, label = str(self.links))

	#Create new chain and modify thickness slider to prevent clipping
	def mod_radius(self,*args):
	
		self.radius = cmds.floatSlider(self.radiusSlider, q = True, v = True)
		cmds.delete(self.chain.delete_chain())
		print self.radius
		chain = Chain(self.links, radius= self.radius, linkRadius= self.radiusLink)
		cmds.floatSlider(self.thicknessSlider, e = True, max = self.radius/3)

	#Create new chain and modify rad slider to prevent clipping
	def mod_thickness(self,*args):
		self.radiusLink = cmds.floatSlider(self.thicknessSlider, q = True, v = True)
		print self.radiusLink
		cmds.delete(self.chain.delete_chain())
		chain = Chain(self.links, radius= self.radius, linkRadius= self.radiusLink)
		cmds.floatSlider(self.radiusSlider, e = True, min= self.radiusLink*3)

	def confirm(self,*args):
		cmds.deleteUI(self.windowName)



	def cancel(self,*args):
		cmds.deleteUI(self.windowName)
		cmds.delete(self.chain.delete_chain())



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
		
	def add_parent(self,parentName):
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
		cmds.setAttr(ring.get_shape() + ".subdivisionsAxis", 4)
		cmds.setAttr(ring.get_transform() + ".rotateY",45) # rotation in xz plane
		
		cmds.polySelect(ring.get_transform(), el = 100) # stretching the square
		cmds.polySelect(ring.get_transform(), el = 85,add = True)
		cmds.polyMoveEdge(translateX = 0.8*(float(-self.radius)*(2.0-math.sqrt(2))/2))

		cmds.polySelect(ring.get_transform(), el = 90)
		cmds.polySelect(ring.get_transform(), el = 95, add = True)
		cmds.polyMoveEdge(translateX =0.8*(float( self.radius)*(2.0-math.sqrt(2))/2))

		#rotate
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
			cmds.parent((self.linkObjs[link]).get_name(),self.linkObjs[0].get_name())
			self.linkObjs[link].add_parent(self.linkObjs[0].get_transform())

	def delete_chain(self):
		rootname = self.linkObjs[0].get_transform()
		cmds.delete(rootname)

		
		

			
		


#Tests
#chain = Chain(20,radius=0.1, linkRadius=0.015)
window = Window()



	