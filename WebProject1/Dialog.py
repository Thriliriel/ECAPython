from DialogNode import DialogNode
import random

class Dialog(object):
	description = ""
	root = None
	currentNode = None
	exitNode = DialogNode("None", "Im sorry but I had dificulty to understand what you said, lets talk about another thing."); #when Arthur/Bella doesnt know what to say
	#Dictionary<string, Node>
	nodes = {}

	def __init__(self, desc):
		self.description = desc
		self.nodes = {}

	def StartDialog(self):
		self.currentNode = self.root

	# --> eu gostava de pizza
    # H: <id> eu gostava de pizza --> EU GOSTO
    #tokenlist: [eu, gosto, pizza]
	def NextSentence(self, tokensList):
		childrenCount = {}

		#put all to minor
		newtokensList = []
		for lis in tokensList:
			newtokensList.append(lis.lower())

		tokensList = newtokensList

		for childId in self.currentNode.GetChildren().keys():
			if childId in childrenCount:
				print("Child ID ("+ childId +") already inserted!")

			childrenCount[childId] = 0

		for childKwLst in self.currentNode.GetChildren():
			for keyword in tokensList:
				value = None
				try:
					value = self.currentNode.GetChildren()[childKwLst].get(keyword)
				except:
					print("Error!")
				if value != None:
					childrenCount[childKwLst] += value

		higher = 0.0
		higherId = ""

		#instantiate new keywords
		for cc in childrenCount:
			if higher < childrenCount[cc]:
				higher = childrenCount[cc]
				higherId = cc

		foundKey = False
		try:
			self.currentNode = self.nodes.get(higherId)
			foundKey = True
		except:
			print("Dialog, 60: Not Found!")
            
		#LOOK HERE!!! SOME SMALLTALKS ARE NOT GOING TO THE RIGHT TREE NODE
		if higherId == "": 
			self.currentNode = self.exitNode; # VICTOR COMMENT: here you can choose a rule to take everytime arthur not find a node with higher ponctuation (maybe polarity)
		
		if not foundKey:
			#throw new ArgumentException("Next utterance not found, supose to be: " + higherId, nameof(higherId));
			#get a random child
			if len(childrenCount) > 0:
				rnd = random.randint(0, len(childrenCount))
				i = 0
				for cc in childrenCount:
					if i == rnd:
						higher = childrenCount[cc]
						higherId = cc
						foundKey = self.nodes.get(higherId)
						break
					i += 1

		#does nothing, so whatever
		#self.ReadCurrentNode()

	def DialogIsOver(self):
		return self.currentNode.IsLeaf()

	def GetSentence(self):
		return self.currentNode.GetSentence()

	def GetId(self):
		return self.currentNode.GetId()

	def GetDescription(self):
		return self.description

	#used to build de dialog
	def AddNode(self, id, content, fatherId):
		if id in self.nodes:
			print("ID already inserted " + id + " must be unique!")
			return

		newNode = DialogNode(id, content)

		if fatherId != "-1":
			fatherRef = None

			try:
				fatherRef = self.nodes.get(fatherId)
			except:
				print("node ID " + fatherId + " dont exist or should be created before ID " + id)

			if fatherRef != None:
				fatherRef.AddChild(id);
				self.nodes[id] = newNode
		else: #root
			self.nodes[id] = newNode
			self.root = self.nodes.get(id) #searching for root

	def AddKeywords(self, id, keywordsList, fatherId):
		if fatherId != "-1":
			if fatherId not in self.nodes:
				print("node ID not found: " + fatherId)
				return
			if id not in self.nodes:
				print("node ID not found: " + id)
				return

			fatherRef = self.nodes[fatherId]

			for kw in keywordsList:
				fatherRef.AddKeyword(id, kw[0], kw[1])

	def Done(self):
		self.currentNode.ResetChildren()

	#check how many cues are inside the nodes of this dialog
	def CheckCuesNodes (self, cues):
		qntFound = 0

		for nd in self.nodes:
			for cue in cues:
				if cues[cue] in self.nodes[nd].GetSentence():
					qntFound += 1

		return qntFound