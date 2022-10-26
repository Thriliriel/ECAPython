from datetime import datetime

class ESK(object):
	#memory information
	#unique ID
	informationID = 0
	#timestamp of the last remembrance
	memoryTime = datetime.now()
	#type of information (5W1H)
	informationType = "Object"
	#information. If text, goes here. If image, assumes the path where they are saved
	information = ""
	#activation, for memory decay and importance definition [0,1]
	activation = 0.0
	#weight (importance) of the memory [0,1]
	weight = 0.0

	def __init__(self, newMT, newInformationType, newInformation, newInformationID, newWeight = 0.0):
		self.memoryTime = newMT
		self.informationType = newInformationType
		self.information = newInformation
		self.activation = 1
		self.informationID = newInformationID
		self.weight = newWeight