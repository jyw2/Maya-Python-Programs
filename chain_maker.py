from maya import cmds

class Ring():
	"""A ring in the chain"""
	def __init__(self,ringNumber,radius,linkRadius):
		(self.transform,self.shape) = cmds.polyTorus(r=radius,sr=linkRadius)
		self.ringNumber = ringNumber
	def get_transform(self):
		return self.transform
	def get_shape(self):
		return self.shape
	def get_ringNumber(self):
		return self.ringNumber
		
			

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

	def move_link(self,ring):
		"""Translate the ring based on its position in the chain."""
		magnitudeOfTranslate = (ring.get_ringNumber())*(self.radius)+(ring.get_ringNumber())*(self.radius-2*(self.linkRadius))
		cmds.move(magnitudeOfTranslate, 0, 0 , ring.get_transform())

	def create_link(self,linknumber):
		"""Creates a ring
			
			Attributes:	
				linkNumber: What number of ring it is(the first is 0,
				second is 1 ... ETC)

			Returns:
				Ring object
		
		"""
		ring = Ring(self.linkNumber,self.radius,self.linkRadius)
		cmds.scale(1,1,self.scale, ring.get_transform())

		print "ringmade"
		if self.rotationState == True:
			cmds.rotate(90 ,0, 0, ring.get_transform())
			
		#Makes the next ring rotate 90 deg
		self.rotationState = not self.rotationState
		self.linkNumber += 1
		
		#stores the ring for later modifications
		self.linkObjs.append(ring)
		self.move_link(ring)
		return ring



		
	# def create_chain:

			
		



chain = Chain(1)
print " ring created"
chain.create_link(1)
chain.create_link(1)
chain.create_link(1)
chain.create_link(1)
chain.create_link(1)
chain.create_link(1)
chain.create_link(1)

	