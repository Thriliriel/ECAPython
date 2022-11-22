from datetime import datetime

class GeneralEvent(object):
	#event information
	#unique ID
	informationID = 0
	#timestamp of the last remembrance
	eventTime = datetime.now()
	#category of the event (belief, person or agent)
	eventType = "agent"
	#what is the event itself (example, what is the interaction exactly?)
	information = ""
	#emotion of this event
	emotion = ""
	#connected nodes, from memory
	nodes = []
	#A positive polarity means that positive answers are expected ("i am good", "yes", and so on...)
	polarity = 0.0

	def __init__(self, newMT, newInformationType, newInformation, newInformationID, newEmotion):
		self.eventTime = newMT
		self.eventType = newInformationType
		self.information = newInformation
		self.informationID = newInformationID
		self.emotion = newEmotion
		self.nodes = []