class IceBreakTree(object):
	id = 0
	ibtype = ""
	question = ""
	parent = None
	child = []
	#if the polarity is true, it means positive (and vice-versa).
	#A positive polarity means that positive answers are expected ("i am good", "yes", and so on...)
	polarity = True

	def __init__(self, id, ibtype, question, polarity):
		self.id = id
		self.ibtype = ibtype
		self.question = question
		self.polarity = polarity
		self.child = []

	def GetId(self):
		return self.id
	
	def SetId(self, id):
		self.id = id

	def GetType(self):
		return self.ibtype

	def GetQuestion(self):
		return self.question

	def GetPolarity(self):
		return self.polarity

	def GetParent(self):
		return self.parent

	def AddChild(self, newChild):
		newChild.SetParent(self)
		self.child.append(newChild)

	def SetParent(self, newParent):
		self.parent = newParent	

	def GetChild(self, index):
		if len(self.child) <= index: 
			return None
		else:
			return self.child[index]

	def FindIcebreaker(self, searchId):
		foundIt = None

		if self.id == searchId: 
			foundIt = self
		else:
			for chdn in self.child:
				if chdn.GetId() == searchId:
					foundIt = chdn
					break
				#else, where its children also
				else:
					it = chdn
					while len(it.child) > 0:
						it = it.child[0]
						if it.GetId() == searchId:
							foundIt = it
							break

					if foundIt != None:
						break

		return foundIt

	#go up the tree and check which child this one is (0, 1, 2...)
	def CheckWhichChild(self, rootParent = 0):
		if self.parent.GetId() == rootParent:
			hereItIs = -1
			for i in range(len(self.parent.child)):
				if self.parent.child[i].GetId() == self.id:
					hereItIs = i
					break
			return hereItIs
		else:
			return self.parent.CheckWhichChild()

	#qnt of children
	def QntChildren(self):
		return len(self.child)