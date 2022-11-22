from Dialog import Dialog
import random
from datetime import datetime

class Topic(object):
	id = ""
	dialogs = [] #using to pick a random dialog 
	busy = False #dialog is running
	currentDialog = None

	def __init__(self, id):
		self.id = id
		self.dialogs = []
		self.busy = False

	#run get next dialog node
	#if its over, finish dialog to sort another one
	#public string RunDialog(double p, string sentence, List<string> memoryDialogs){
	def RunDialog(self, p, tokenizeSentence, memoryDialogs):
		if self.currentDialog.DialogIsOver():
			self.CloseDialog()
			return None

		if p != 0:
			self.currentDialog.NextSentence(tokenizeSentence)

		#check if already used
		#UnityEngine.Debug.Log(_identificator + "-" + currentDialog.GetDescription() + "-" + currentDialog.GetId().ToString());
		while self.id + "-" + self.currentDialog.GetDescription() + "-" + self.currentDialog.GetId() in memoryDialogs:
			#get next
			#currentDialog.NextSentence(p, sentence);
			self.currentDialog.NextSentence(tokenizeSentence)

			#check leaf, if so break
			if self.currentDialog.DialogIsOver():
				break

		return self.currentDialog.GetSentence()

	#search for other dialog routine
	def StartNewDialog(self, emotion = ""):
		self.currentDialog = self.GetDialog(emotion)
		if self.currentDialog != None:
			self.ChangeState()
			self.currentDialog.StartDialog()

	#internal function to finish a dialog
	def CloseDialog(self):
		if self.currentDialog in self.dialogs:
			self.dialogs.remove(self.currentDialog)
		#self.ChangeState()
		self.busy = False

	# choose new dialog
	# obs: next version it woundn´t be random dialog
	def GetDialog(self, emotion = ""):
		if len(self.dialogs) == 0:
			return None

		#if we have emotion, we need to find the correct dialog. Otherwise, it can be random.
		index = -1
		if emotion == "":
			rnd = random.randint(0, len(self.dialogs)-1)
			index = rnd
			#var rnd = new System.Random(DateTime.Now.Millisecond);
			#index = rnd.Next(0, dialogs.Count);
		else:
			#happiness, sadness
			i = 0
			for dia in self.dialogs:
				if emotion in dia.GetDescription():
					index = i
					break
				i += 1

			#if did not find, get random, whatever!
			if index == -1:
				rnd = random.randint(0, len(self.dialogs)-1)
				index = rnd
				#var rnd = new System.Random(DateTime.Now.Millisecond);
				#index = rnd.Next(0, dialogs.Count);

		#print(index)
		d = self.dialogs[index]
		self.dialogs.remove(d)
		return d

	def ChangeState(self):
		self.busy = not self.busy

	#for verification if a dialog is happening
	def IsDialoging(self):
		return self.busy

	def IsDialogsAvailable(self):
		return len(self.dialogs) != 0

	def GetId(self):
		return self.id

	def GetLengthDialogs(self):
		return len(self.dialogs)

	def GetCurrentDialog(self):
		return self.currentDialog

	# Add new dialog
	def InsertDialog(self, d):
		self.dialogs.append(d)