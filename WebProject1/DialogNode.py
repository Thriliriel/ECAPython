from curses import has_key


class DialogNode(object):
	id = ""
	sentence = ""
	#Dictionary<string, WeightWords>
	#WeigthWords: Dictionary<string, double>
	children = {} #< child_id, <..> >

	def __init__(self, id, st):
		self.id = id
		self.sentence = st
		self.children = {}

	def AddChild(self, childId):
		if not self.children.has_key(childId):
			self.children[childId] = {}
		else:
			print("Child ID ("+ childId +") already used at this node! (internal error)")

	def AddKeyword(self, childId, keyword, weight):
		value = {}

		try:
			value = self.children.get(childId)
		except:
			print("Child ID ("+ childId +") not found! (internal error)")

		if value.has_key(keyword):
			print("Keyword " + keyword + " already used in " + childId + ". Keyword must be unique for each ID!")
		else:
			self.children[childId][keyword] = weight

	def GetId(self):
		return self.id

	def GetSentence(self):
		return self.sentence

	def GetChildren(self):
		return self.children

	def IsLeaf(self):
		return len(self.children) == 0

	def ResetChildren(self):
		self.children.clear()