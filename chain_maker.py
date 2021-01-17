from maya import cmds
import math



class Window:
	"""Creates a window"""
	def __init__(self):
			
		self.windowName = "chainWindow"

		#if window already exists
		if cmds.window(self.windowName, ex = True):
			self.cancel()

		#Initiate chain and window
		self.chain = Chain(1)
		cmds.window(self.windowName,iconName = "Chain Maker")
		
		#build UI
		cmds.columnLayout(adjustableColumn = True, co = ("both",100),rs = 30)

		cmds.text("Number of Links" )
		self.linksSlider = cmds.intSlider(min = 1, max = 100, value = 1, dc = self.mod_links)
		
		cmds.text("Radius of Links")
		self.radiusSlider = cmds.floatSlider(min = 0.01, max = 2, value = 0.5 , dc = self.mod_radius)

		cmds.text("Radius of Thickness of Links")
		self.thicknessSlider = cmds.floatSlider(min = 0.0001, max = 0.5, value = 0.05 , dc = self.mod_thickness)


		
		cmds.button("Confirm", c =self.confirm)

		cmds.button("Cancel", c = self.cancel)

		cmds.showWindow()

	def mod_links(self,*args):
		newLinks = cmds.intSlider(self.linksSlider, q = True, v = True)
		self.chain.change_chain(links = newLinks)

	def mod_radius(self,*args):
		newRadius = cmds.floatSlider(self.radiusSlider, q = True, v = True)
		self.chain.change_chain(length = newRadius)

	def mod_thickness(self,*args):
		newLinkRadius = cmds.floatSlider(self.thicknessSlider, q = True, v = True)
		self.chain.change_chain(thickness= newLinkRadius)


	# def printt(self,*args):
	# 	print cmds.floatSlider(self.thickness, value = True, q=True)

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
		print self.transform
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
			print (self.linkObjs[link]).get_name()
			cmds.parent((self.linkObjs[link]).get_name(),self.linkObjs[0].get_name())
			self.linkObjs[link].add_parent(self.linkObjs[0].get_transform())

	def change_chain(self, links = None, length = None, thickness = None):
		"""modifies the chain properties. Links, length and thickness can 
		all be changed. EX: change_chain(self, links = int, length = float, thickness = float) """
		#link number is flagged to change
		if links:

			changeInLinks = links - self.links

			self.links = links

			#if missing links create and parent links
			if changeInLinks >0:

				for link in range(changeInLinks):

					newRing = self.create_link()
					cmds.parent(newRing.get_name(),self.linkObjs[0].get_name())
					newRing.add_parent(self.linkObjs[0].get_transform())

			#if too many links. Ensure the root node is not deleted
			elif changeInLinks < 0 and self.links > 1:
				self.linkObjs[len(self.linkObjs)-1].delete_link()
				self.linkNumber -= 1
				self.linkObjs.pop()


				
		#length is flagged to change
		if length:
			for ring in self.linkObjs:
				#reset the link to 0 for easier re-transform
				magnitudeOfTranslate = (ring.get_ringNumber())*(self.radius)+(ring.get_ringNumber())*(self.radius-2*(self.linkRadius))
				cmds.move(-magnitudeOfTranslate, 0, 0 , ring.get_transform())
				
			changeInRadius = self.radius - length

			for ring in self.linkObjs:
				# Prepare the variables for transforming
				# pastTransformX = 0.8*(float(-self.radius)*(2.0-math.sqrt(2))/2)
				
				self.radius = length

				# newTransformX = 0.8*(float(-self.radius)*(2.0-math.sqrt(2))/2)

				#reshape
				cmds.polySelect(ring.get_transform(), el = 100) # stretching the square
				cmds.polySelect(ring.get_transform(), el = 85,add = True)
				cmds.polyMoveEdge(translateX = (changeInRadius))

				cmds.polySelect(ring.get_transform(), el = 100) # stretching the square z
				cmds.polySelect(ring.get_transform(), el = 95,add = True)
				cmds.polyMoveEdge(translateZ = (changeInRadius))


				cmds.polySelect(ring.get_transform(), el = 90)
				cmds.polySelect(ring.get_transform(), el = 95, add = True)
				cmds.polyMoveEdge(translateX = -(changeInRadius))

				cmds.polySelect(ring.get_transform(), el = 85) # stretching the square z
				cmds.polySelect(ring.get_transform(), el = 90,add = True)
				cmds.polyMoveEdge(translateZ = -(changeInRadius))


				self.move_link(ring)

				


		#thickness is flagged to change.
		if thickness:
			for ring in self.linkObjs:
				#reset the link to 0 for easier re-transform
				magnitudeOfTranslate = (ring.get_ringNumber())*(self.radius)+(ring.get_ringNumber())*(self.radius-2*(self.linkRadius))
				cmds.move(-magnitudeOfTranslate, 0, 0 , ring.get_transform())

				# Prepare the variables for transforming
				pastTransformX = 0.8*(newTransformX - pastTransformX)

				self.linkRadius = thickness

				newTransformX = -0.8*(newTransformX - pastTransformX)

				#reshape
				cmds.polySelect(ring.get_transform(), el = 100) # stretching the square
				cmds.polySelect(ring.get_transform(), el = 85,add = True)
				cmds.polyMoveEdge(translateX = 0.8*(newTransformX - pastTransformX))

				cmds.polySelect(ring.get_transform(), el = 90)
				cmds.polySelect(ring.get_transform(), el = 95, add = True)
				cmds.polyMoveEdge(translateX =-0.8*(newTransformX - pastTransformX))

				self.move_link(ring)

	def delete_chain(self):
		rootname = self.linkObjs[0].get_transform()
		cmds.delete(rootname)

		
		

			
		


#Tests
#chain = Chain(20,radius=0.1, linkRadius=0.015)
window = Window()



	