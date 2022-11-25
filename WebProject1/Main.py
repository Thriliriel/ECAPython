from PAD import PAD
from Topic import Topic
from Dialog import Dialog
import random
from datetime import datetime
from GeneralEvents import GeneralEvent
from ESK import ESK
from Vector3 import Vector3
from IceBreakTree import IceBreakTree
import requests

class Main(object):
	#attributes
	#PAD
	pad = None
	#FPS for update
	fps = 1
	#list of topics
	topics = []
	#list of topics (do not change)
	topicsFinal = []
	#current topic
	currentTopic = None
	#ice breakers
	iceBreakers = None
	#is breaking ice?
	isBreakingIce = False
	#id of the icebreaker in use
	usingIceBreaker = 0
	#id of the actual root icebreaker, if it is going down the tree
	rootIceBreaker = 0
	#list with all dialogs/topics in memory
	dialogsInMemory = []
	dialogsAnswersInMemory = []
	#list with dialogs already used
	dialogsUsed = []
	#Dictionary<string, List<Tuple<string, double>>> 
	keywordsDataset = {}
	#name of the user
	personName = "User"
	#id of the user
	personId = None
	#name of the agent
	agentName = "Bella"
	#can arthur speak?
	canSpeak = True
	#using empathy? (for this project, dont think so in the beginning)
	usingEmpathy = False
	#chatlog to save
	chatLog = ""
	#is agent bored?
	isBored = False
	#last sentence polarity found
	lastPolarity = 0
	#list with the 5 last polarities
	#lastPolarities = []
	#is it chat only mode?
	chatMode = False
	#key for online chatbot
	apiKey = "Bearer 1fbdeab9-3742-4fcb-acc7-0da3f2bb2ae9"
	#save a new memory node?
	saveNewMemoryNode = False
	#timer for small talk
	idleTimer = 0
	#emotion of the agent
	agentEmotion = ""
	#array with the last framesToConsider emotions found, and respective valences
	foundEmotions = []
	#who did the agent already greeted?
	peopleGreeted = []
	#agent memory
	#following George Miller definition, each person is able to keep 7 pieces of information in memory at each time, varying more or less 2
	agentShortTermMemory = {}
	memorySpan = 15
	#long term memory, with the node information
	agentLongTermMemory = {}
	#general events
	agentGeneralEvents = {}
	#memory ids
	nextEpisodeId = 0
	nextEskId = 0
	#personality
	personality = []
	#what was the last interaction of the user?
	lastInteraction = ""
	#yes/no question
	isYesNoQuestion = False
	#using memory?
	isUsingMemory = True
	#retrieving memory?
	isRetrievingMemory = False
	#webService path
	#webServicePath = "http://vhlab.lad.pucrs.br:5001/"
	webServicePath = "http://localhost:5000/"

	def Awake(self):

		#random agent
		rnd = random.randrange(10)
		if rnd % 2 == 0: 
			self.agentName = "Arthur"
		else: 
			self.agentName = "Bella"
			
		#if Arthur is in chat mode, we can deactivate all graphical stuff
		if self.chatMode:
			self.canSpeak = False
			
		#set the ice breakers
		self.rootIceBreaker = -1
		self.usingIceBreaker = -1
		#first element is just the pointer to the root questions
		self.iceBreakers = IceBreakTree(0, "root", "", False)
		self.usingIceBreaker = 0

		#load icebreakers and answers from the file
		self.LoadIceBreakersAndStuff()

		#set the small talks
		self.LoadKeywords()
		self.LoadSTs()

		for tg in self.topics:
			self.topicsFinal.append(tg)

		#load small talks from the memory
		self.LoadMemoryDialogs()

		self.PickTopic()

		##if UNITY_EDITOR_WIN || UNITY_STANDALONE_WIN || UNITY_EDITOR_OSX || UNITY_STANDALONE_OSX || UNITY_XBOXONE
		##start the prolog
		##prolog = new PrologEngine(persistentCommandHistory: false);
		##prologStatements = new Dictionary<string, int>();
		##endif

		#what we have on textLTM, load into auxiliary LTM
		self.LoadEpisodicMemory()

		#after loading the memory, we update it depending on if it is Arthur or Bella
		if self.agentName == "Arthur" and self.agentLongTermMemory[1].information == "Bella":
			self.agentLongTermMemory[1].information = "Arthur"
			self.agentLongTermMemory[2].information = "AutobiographicalStorage/Images/Arthur.png"
		elif self.agentName == "Bella" and self.agentLongTermMemory[1].information == "Arthur":
			self.agentLongTermMemory[1].information = "Bella"
			self.agentLongTermMemory[2].information = "AutobiographicalStorage/Images/Bella.png"

		##if UNITY_EDITOR_WIN || UNITY_STANDALONE_WIN || UNITY_EDITOR_OSX || UNITY_STANDALONE_OSX || UNITY_XBOXONE
		##create the facts from the memory
		#CreateFactsFromMemory();
		##endif

		#read the next ID from the file
		#first line: ESK Ids. Second line: Episode Ids
		fl = open("nextId.txt")
		idezinhos = fl.read().split('\n')
		fl.close()
		self.nextEpisodeId = idezinhos[1]
		self.nextEskId = idezinhos[0]
		##if UNITY_EDITOR_WIN || UNITY_STANDALONE_WIN || UNITY_EDITOR_OSX || UNITY_STANDALONE_OSX || UNITY_XBOXONE
		##load prolog beliefs
		#LoadBeliefs();
		##endif		

		#start stuff
		self.LoadPersonality()

		#reset the result file
		file_to_delete = open("resultFile.txt",'w')
		file_to_delete.close()

		#reset the result token files
		self.ResetTokenFiles()

		#short-term memory co-routine
		#memory decay and removal after 15 seconds. TODO
		#StartCoroutine(ControlSTM());

		#start the idle timer with the seconds now
		self.idleTimer = datetime.now()

		#first smalltalk
		#self.SmallTalking([])

		#meet
		self.MeetNewPeople()

	def LoadKeywords(self):
		fl = open("keywords.txt")
		keyWords = fl.read().split('\n')
		fl.close()
		#print(keyWords[0])

		#Dictionary<string, List<Tuple<string, double>>>(); # node_id [(word, weight) ..]
		self.keywordsDataset = {}
		for kw in keyWords:
			if kw == "" or kw == None: 
				continue

			line = kw.strip()
			data = line.split(' ')

			nodeId = data[0].strip()
			if nodeId not in self.keywordsDataset:
				self.keywordsDataset[nodeId] = []
		
			self.keywordsDataset[nodeId].append([data[1].strip(), float(data[2].strip())])


	def LoadSTs(self):
		fl = open("smallTalk.txt")
		smallT = fl.read().split('\n')
		fl.close()

		#print (smallT)

		self.topics = []
		currentTopic = None
		currentDialog = None

		dialogIds = []

		for line in smallT:
			if line == "":
				continue

			line = line.strip()

			command = line[0]

			#new topic
			if command == '$':
				currentTopic = Topic(line[2:len(line)])
				self.topics.append(currentTopic)
			elif command == '[': #new dialog
				currentDialog = Dialog(line[2:len(line)])
			elif command == '#': #dialog
				#currentDialog = Dialog(line[2:len(line)])

				#id, sentence, polarity, isLeaf, father id, memory edge, memory node value..
				data = line.split(';')
				nodeId = data[0][2:len(data[0])].strip()
				fatherId = data[2].strip()

				if nodeId in dialogIds:
					print("PARSER ERROR: Node id already used (must be unique!): " + nodeId)
					return

				currentDialog.AddNode(nodeId, data[1].strip(), fatherId)
				dialogIds.append(nodeId)

				#root has no parent
				if fatherId == "-1": 
					continue
			
				try:
					lst = self.keywordsDataset[nodeId]
					currentDialog.AddKeywords(nodeId, lst, fatherId)
				except Exception as e:
					print("PARSER ERROR: Node id not found: " + nodeId)
					print(e)
					return
			#close dialog (insert on topic)
			elif command == ']':
				currentTopic.InsertDialog(currentDialog)

		self.keywordsDataset.clear()

	#load small talks saved in memory
	def LoadMemoryDialogs(self):
		fl = open("AutobiographicalStorage/smallTalksUsed.txt")
		stu = fl.read().split('\n')
		fl.close()

		for line in stu:
			if line != "" and line != None:
				self.dialogsUsed.append(line)

	#new small talking
	def PickTopic(self, whichTopic = ""):
		#equal 1, because the emotion topic is not pickable
		if len(self.topics) == 1:
			return

		#if it is random topic
		if whichTopic == "":
			index = random.randrange(len(self.topics))
			self.currentTopic = self.topics[index]

			#emotions is not pickable
			while "emotions" in self.currentTopic.GetId():
				index = random.randrange(len(self.topics))
				self.currentTopic = self.topics[index]

			self.topics.remove(self.currentTopic)
		#else, it is a chosen topic
		else:
			ind = 0
			self.currentTopic = self.topics[ind]
			while self.currentTopic.GetId() != whichTopic:
				ind += 1
				if ind >= len(self.topics):
					break

				self.currentTopic = self.topics[ind]

	def SmallTalking(self, tokenizeSentence, useThis = None, beforeText = ""):
		if self.currentTopic == None or self.topics == None:
			return

		#if topics is empty, we are done
		if len(self.topics) == 0 and not self.currentTopic.IsDialogsAvailable() and self.currentTopic.GetCurrentDialog().DialogIsOver():
			self.currentTopic.CloseDialog()
			return

		ct = None
		self.idleTimer = datetime.now()
		self.saveNewMemoryNode = False
		first = False

		if not self.currentTopic.IsDialoging(): #sort new dialog
			if (not self.currentTopic.IsDialogsAvailable()): #there isnt available dialogs in current topic
			#if already chosen, use it
				if useThis != None:
					#find the topic of this dialog
					for tp in self.topics:
						for dl in tp.dialogs:
							if dl.GetDescription() == useThis.GetDescription():
								self.currentTopic = tp
								break
				else: #just follow the usual flow
					self.PickTopic()

			#just to be sure
			#if already chosen, use it
			if useThis != None:
				#find the topic of this dialog
				for tp in self.topics:
					for dl in tp.dialogs:
						if dl.GetDescription() == useThis.GetDescription():
							self.currentTopic = tp
							break

			#if the topic is emotions, we pass the self.agentEmotion together to select the appropiate dialog
			if self.currentTopic.GetId() == "emotions":
				print(self.agentEmotion)
				self.currentTopic.StartNewDialog(self.agentEmotion)
			elif useThis != None:
				self.currentTopic.StartNewDialog(useThis.GetDescription())
			else:
				self.currentTopic.StartNewDialog()

			first = True

		if first:
			#if it is first, check if the dialog tree was already used
			if self.currentTopic.GetId() + "-" + self.currentTopic.GetCurrentDialog().GetDescription() + "-" + self.currentTopic.GetCurrentDialog().GetId() in self.dialogsUsed:
				self.currentTopic.CloseDialog()
				ct = None

				#if has no more dialogs, topic is gone as well
				if self.currentTopic.GetLengthDialogs() == 0:
					self.currentTopic.GetCurrentDialog().Done()
			else:
				ct = self.currentTopic.RunDialog(0, tokenizeSentence, self.dialogsUsed)
		else:
			ct = self.currentTopic.RunDialog(self.lastPolarity, tokenizeSentence, self.dialogsUsed)

		if ct != None:
			digmem = self.currentTopic.GetId() + "-" + self.currentTopic.GetCurrentDialog().GetDescription() + "-" + self.currentTopic.GetCurrentDialog().GetId()
        
			if digmem not in self.dialogsUsed and self.currentTopic.GetId() != "emotions":
				self.dialogsUsed.append(digmem)
			if digmem not in self.dialogsInMemory and self.currentTopic.GetId() != "emotions":
				self.dialogsInMemory.append(digmem)
				self.SpeakYouFool(ct)
			if self.currentTopic.GetId() == "emotions":
				self.SpeakYouFool(ct)

		print(ct)

	#try to find a specific smalltalk
	def FindSmallTalk(self, cues):
		qntFound = 0
		dialFound = None
		for tp in self.topicsFinal:
			for dl in tp.dialogs:
				ndFound = dl.CheckCuesNodes(cues)

				if ndFound > qntFound:
					qntFound = ndFound
					dialFound = dl

		return dialFound

	#Agent says something
	def SpeakYouFool(self, weirdThingToTalk):
		newText = "<b>" + self.agentName + "</b>: " + weirdThingToTalk + "\n"
		#chatText.text += newText;

		#add in chat log
		self.chatLog += newText

		#just speak if canSpeak is true
		#if self.canSpeak:
			#also, speak it
			#sc.GetComponent<SpeakerController>().SpeakSomething(weirdThingToTalk)

	#Load Episodic memory
	def LoadEpisodicMemory(self):
		fl = open("AutobiographicalStorage/episodicMemory.txt")
		em = fl.read().split('\n')
		fl.close()

		readingESK = True
		for line in em:
			#when we read the dividing sequence "%%%", episodes start
			if line == "%%%":
				readingESK = False
				continue

			if line != "" and line != None:
				info = line.split(';')
				ide = int(info[0])
				
				#while it is reading ESK
				if readingESK:
					#timestamp, newInformationType, newInformation, newInformationID, newWeight
					newMem = ESK(datetime.strptime(info[1].strip(), "%d/%m/%Y %I:%M:%S %p"), info[3], info[2], ide, float(info[5]))

					#LTM - everything
					self.agentLongTermMemory[ide] = newMem
				#else, it is episodes
				else:
					#timestamp, newInformationType, newInformation, newInformationID, newEmotion
					newGen = GeneralEvent(datetime.strptime(info[1], "%d/%m/%Y %I:%M:%S %p"), info[2], info[3], ide, "")
					newGen.polarity = float(info[4])

					#add the associated nodes of this episode
					memNodes = info[5].split('_')
					for nod in memNodes:
						newGen.nodes.append(self.agentLongTermMemory[int(nod)])
					
					#add
					self.agentGeneralEvents[ide] = newGen

	#Load Personality
	def LoadPersonality(self):
		fl = open("personality.txt")
		info = fl.read().split(';')
		fl.close()

		if len(info) != 5:
			print("File incomplete, fix it and try again!")
		else:
			for inf in info:
				self.personality.append(float(inf))

		#depending on the personality, we assign an initial PAD space
		#In the second condition (i.e. extrovert), she is assigned a controlled
		#extrovert personality as her PPAD at (80, 50, 100). These values are set
		#based on the characteristics of extroverted people given by McCrae
		#et al. [39], in which they are deemed to have a tendency towards positive emotion (P 80), are seeking excitement (A 50), 
		#and are assertive (D 100).
		if self.personality[2] >= 0.5:
			self.pad = PAD(0.8, 0.5, 1)

			#if it has some N, it means it is a bit "paranoid".. so, lets reduce its dominance
			if self.personality[4] > 0.5:
				self.pad.SetDominance(0.5)

		#In the third condition (i.e. introvert), the ECA is assigned a controlled introvert personality as her PPAD at (−80, 30, −100), based on
		#the characteristics of introvert people [39], which are characterized by
		#a tendency towards negative emotion (P −80), low excitement seeking
		#(A 30), and low assertiveness (D −100).
		else:
			self.pad = PAD(-0.8, 0.3, -1)

			#if it has little N, it means it is not "paranoid".. so, lets raise its dominance
			if self.personality[4] > 0.5:
				self.pad.SetDominance(-0.5)

		print("Initial PAD: " + str(self.pad.GetPleasure()) + " - " + str(self.pad.GetArousal()) + " - " + str(self.pad.GetDominance()));

		chosenEmo = self.FindPADEmotion()
		
		self.SetEmotion(chosenEmo.lower())

	#load the icebreakers and respective answers
	def LoadIceBreakersAndStuff(self):
		fl = open("icebreakers.txt")
		iceBreak = fl.read().split('\n')
		fl.close()
		
		for line in iceBreak:
			#if it has #, it is comments
			if line == "" or "#" in line:
				continue

			info = line.split(';')
			ibId = int(info[0])
			ibType = info[1]
			ibQuestion = info[2]
			ibPolarity = bool(info[3])
			ibParent = int(info[4])

			#if parent is 0, is one of the primary ones
			if ibParent == 0:
				self.iceBreakers.AddChild(IceBreakTree(ibId, ibType, ibQuestion, ibPolarity))
			#otherwise, it is one of the secondary ones. Need to first find the parent and, then, add
			else:
				self.iceBreakers.FindIcebreaker(ibParent).AddChild(IceBreakTree(ibId, ibType, ibQuestion, ibPolarity))

	#find the closest emotion from PAD
	def FindPADEmotion(self):
		chosenEmo = ""

		#to check possible new emotion, we check all pad emotions and the distance of PAD from them. We choose the closest.
		minDistance = -1
		for pe in self.pad.padEmotions:
			dist = Vector3.Distance(Vector3(self.pad.GetPleasure(), self.pad.GetArousal(), self.pad.GetDominance()), self.pad.padEmotions[pe])
			#if it is the first, just take it
			if minDistance == -1:
				minDistance = dist
				chosenEmo = pe
			else:
				#if distance is smaller, it is the new favorite
				if dist < minDistance:
					minDistance = dist
					chosenEmo = pe

		#anger, disgust, fear, happiness, sadness, surprise
		print("New Emo: " + chosenEmo)

		if chosenEmo == "Friendly" or chosenEmo == "Joyful" or chosenEmo == "Happy":
			chosenEmo = "joy"
		elif chosenEmo == "Angry" or chosenEmo == "Enraged":
			chosenEmo = "anger"
		elif chosenEmo == "Surprised":
			chosenEmo = "surprise"
		elif chosenEmo == "Fearful":
			chosenEmo = "fear"
		elif chosenEmo == "Depressed" or chosenEmo == "Sad" or chosenEmo == "Frustrated":
			chosenEmo = "sadness"
		elif chosenEmo == "Bored":
			chosenEmo = "bored"

		return chosenEmo

	def SetEmotion(self, emotion):
		#MAYBE WITH CAM ONE DAY
		#if it is setting emotion, it means it found a face. So, let us find out whom face it is
		#if self.personName == "" and self.agentEmotion == "":
			#StartCoroutine(RecognitionWebService());

		self.agentEmotion = emotion

		if self.agentEmotion != "":
			if self.agentEmotion == "joy":
				self.agentEmotion = "happiness"

			#just change facial expression if empathy is being used
			if self.usingEmpathy:
				#if Arthur, play
				if self.agentName == "Arthur" and not self.chatMode:
					emoAnim = self.agentEmotion + "_A"

					#mariano.GetComponent<CharacterCTRL>().PlayAnimation(emoAnim);
				elif self.agentName == "Bella" and not self.chatMode:
					#play bella
					emoAnim = self.agentEmotion + "_A"

	#reset token files
	def ResetTokenFiles(self):
		file_to_delete = open("resultTokenFile.txt",'w')
		file_to_delete.close()
		file_to_delete = open("textToTokenFile.txt",'w')
		file_to_delete.close()

	#new version of SendRequestChat
	def SendRequestChat(self, textSend):
		newText = "<b>" + self.personName + "</b>: " + textSend + "\n"

		#add to chat log
		self.chatLog += newText

		#print(self.chatLog)

		#reset the idle timer
		self.idleTimer = datetime.now()

		self.lastInteraction = textSend

		#if the len is different, the user is answering a small talk. Save
		if len(self.dialogsAnswersInMemory) != len(self.dialogsInMemory):
			self.dialogsAnswersInMemory.append(self.lastInteraction)

		#first letter to lower
		textSend = self.FirstLetterToLower(textSend)

		#we can change a bit some common sentences, to make it easier to understand
		if textSend == "how are you?":
			textSend = "how are you feeling?"

		#if it it some common questions, can already answer
		if "who" in textSend and "you" in textSend:
			self.SpeakYouFool("I am " + self.agentName)
		elif "your" in textSend and "name" in textSend:
			self.SpeakYouFool("My name is " + self.agentName)
		#else, keep going
		else:
			#UPDATE: we always tokenize now, and treat things in the update
			#UPDATE: now we send a request to our webservice, through a json
			self.TokenizationWebService(textSend)
			#TokenizationWebService(textSend);

	#Web Service for Tokenization
	def TokenizationWebService(self, sentence):
		# defining the api-endpoint 
		API_ENDPOINT = self.webServicePath + "tokenize"
  
		# your API key here (TODO: WE NEED TO CREATE ONE, USING THIS JUST FOR NOW)
		API_KEY = self.apiKey
  
		# data to be sent to api
		data = {'api_dev_key':API_KEY,
				'text':[sentence]}
  
		# sending post request and saving response as response object
		r = requests.post(url = API_ENDPOINT, json = data)
  
		# extracting response text 
		result = r.text
		print("Result: " + result)

		#Result: "{\"0\":{\"0\":\"i\",\"1\":\"love\",\"2\":\"fry\",\"3\":0.6369},\"1\":{\"0\":\"NN\",\"1\":\"VBP\",\"2\":\"NN\",\"3\":0}}"

		#need to format it properly now
		info = result.replace('"', '')
		info = info.replace("\\", "")
		info = info.replace("{", "")
		info = info.replace("0:0", "0")
		info = info.replace("1:0", "0")
		infoSplit = info.split('}')
		#print(infoSplit)

		tokensKey = infoSplit[0].split(',')
		tknType = infoSplit[1].split(',')
		tknType = tknType[1:len(tknType)]

		print(tokensKey)
		print(tknType)

		#assemble!
		tokens = {}
		for i in range(len(tokensKey)):
			ts1 = tokensKey[i].split(':')

			if len(tknType) > 0:
				ts2 = tknType[i].split(':')
			else:
				ts2 = [0, 0]

			if len(ts1) > 1:
				t1 = ts1[1]
			else:
				t1 = ts1[0]
			if len(ts2) > 1:
				t2 = ts2[1]
			else:
				t2 = ts2[0]
				
			tokens[t1] = t2

		print(tokens)

		emoTalk = False

		#if it has tokens, we try to make a generative retrieval
		if tokens != None:
			#change some tokens, if exists
			if "you" in tokens and self.agentName not in tokens:
				tokens.pop("you")
				tokens[self.agentName] = "NNP"
			if "yourself" in tokens and self.agentname not in tokens:
				tokens.pop("yourself")
				tokens[self.agentName] = "NNP"
			if "i" in tokens:
				tokens.pop("i")
				tokens[self.personName] = "NNP"
			if "me" in tokens:
				tokens.pop("me")
				tokens[self.personName] = "NNP"
			if "myself" in tokens:
				tokens.pop("myself")
				tokens[self.personName] = "NNP"
			if "my" in tokens and "name" in tokens:
				tokens.pop("my")
				tokens[self.personName] = "NNP"
			if "your" in tokens and "name" in tokens:
				tokens.pop("your")
				tokens[self.agentName] = "NNP"

			if "bore" in tokens or "afraid" in tokens or "happy" in tokens or "sad" in tokens or "surprised" in tokens or "disgusted" in tokens	or "angry" in tokens:
				tokens.append("feel", "VB")

			#check if it is a question
			isQuestion = False
			for key in tokens:
				if key == "?":
					isQuestion = True
					break

			#if we identified it as being a question and it is inside a smalltalk, we break
			if isQuestion and self.currentTopic.IsDialoging():
				self.currentTopic.CloseDialog()

			#if the person is asking about the feelings of the agent, we start the related emotional smalltalk
			if isQuestion and self.agentName in tokens and ("feel" in tokens or "feels" in tokens):
				self.PickTopic("emotions")
				emoTalk = True
			#else if (!isGettingInformation && isKnowingNewPeople)
			#{
			#	SaveNewPerson(tokens);
			#	isUsingMemory = false;
			#}
			elif not self.currentTopic.IsDialoging():
				#if it is a question, we do not save it. Otherwise, yeap
				self.saveNewMemoryNode = True
				if isQuestion: 
					self.saveNewMemoryNode = False

				self.GenerativeRetrieval(tokens)

			#is using memory, go on
			if self.isUsingMemory:
				informationEvent = ""
				
				#save it
				#if self.saveNewMemoryNode:
					#SaveMemoryNode(tokens, informationEvent)

				if self.currentTopic.IsDialoging():
					asToki = []
					for key in tokens:
						asToki.append(key)
					self.SmallTalking(asToki)
		
		
	def FirstLetterToLower(self, text):
		if text == None:
			return None

		if len(text) > 1:
			return str(text[0].lower()) + text[1:len(text)]

		return text.lower()

	#retrieve a memory based on cues
	def GenerativeRetrieval(self, cues):
		#first of all, we can take some things out, like interrogation mark and other elements
		if "?" in cues:
			cues.pop("?")
		if "be" in cues: 
			cues.pop("be")
			
		auxCues = {}
		for cue in cues:
			if cue == "old" or cue == "age":
				auxCues["born"] = cues[cue]
			elif cue == "working":
				auxCues["work"] = cues[cue]
			elif cue == "studying":
				auxCues["study"] = cues[cue]
			elif cue == "children" or cue == "kids": 
				auxCues["has children"] = cues[cue]            
			else:
				auxCues[cue] = cues[cue]

		cues = auxCues

		#look for similar words
		textParam = ""
		for cue in cues:
			if textParam == "": 
				textParam = cue
			else:
				textParam += "-" + cue

		#before sending, lets see the nouns, which we try to use as topics :D
		topicSent = []
		for cu in cues:
			if cues[cu] == "NN":
				topicSent.append(cu)
			elif cues[cu] == "NNP" and cu != self.personName and cu != self.agentName:
				topicSent.append(cu)		

		#there was some prolog stuff here, removed...
		foundProlog = False
		if not foundProlog:
			#retrieving memory
			self.isRetrievingMemory = True

			self.WordVecWebService(textParam, cues)

	#Web Service for Word2Vec
	def WordVecWebService(self, sentence, cues):
		#before sending, lets see the nouns to guess the topic
		topicSent = []
		for cu in cues:
			if cues[cu] == "NN":
				topicSent.append(cu)
			elif cues[cu] == "NNP" and cu != self.personName and cu != self.agentName:
				topicSent.append(cu)
		
		# defining the api-endpoint 
		API_ENDPOINT = self.webServicePath + "similarWords"
  
		# your API key here (TODO: WE NEED TO CREATE ONE, USING THIS JUST FOR NOW)
		API_KEY = self.apiKey
  
		# data to be sent to api
		data = {'api_dev_key':API_KEY,
				'text':[sentence]}
  
		# sending post request and saving response as response object
		r = requests.post(url = API_ENDPOINT, json = data)
  
		# extracting response text 
		result = r.text
		print("Result: " + result)
		#['0:em,1:to,2:show,3:as,4:block,5:pasta,6:chocolate,7:sushi,8:starbucks,9:nutella,10:,11:,12:,13:,14:,15:,16:,17:,18:,19:', ',0.8832516074,0.871879518,2:0.8496714234,3:0.8486312032,4:0.8383049965,5:0.9345267415,6:0.9283044338,7:0.9267594814,8:0.9123665094,9:0.8918703794,10.0,10.0,12:0.0,13:0.0,14:0.0,15:0.0,16:0.0,17:0.0,18:0.0,19:0.0', '', '']

		#need to format it properly now
		info = result.replace('"', '')
		info = info.replace("\\", "")
		info = info.replace("{", "")
		info = info.replace("0:0", "0")
		info = info.replace("1:0", "0")
		infoSplit = info.split('}')
		stuff = infoSplit[0]
		stuff2 = infoSplit[1]
		terms = stuff.split(',')
		similarities = stuff2.split(',')
		print(terms)

		tokens = []
		tknType = []
		for key in terms:
			if len(key) > 0:
				splita = key.split(':')
				if len(splita) > 1:
					tokens.append(splita[1])

		for key in similarities:
			if len(key) > 0 and key != "0":
				splita = key.split(':')
				if len(splita) > 1:
					tknType.append(float(splita[1]))

		#organize cues with similars
		newCues = {}

		#each cue has 5 results. So, we take for each of them
		qntCue = 0
		for cu in cues:
			if cu not in newCues:
				newCues[cu] = cues[cu]

			#we just actually use for NN
			if cues[cu] == "NN":
				#5 of this cue
				for i in range (5):
					#ALSO, we just add if the similarity is over 60%
					if tknType[5*qntCue+i] > 0.6:
						if tokens[5 * qntCue + i] not in newCues:
							newCues[tokens[5 * qntCue + i]] = cues[cu]
			qntCue += 1

		cues = newCues

		#making a test: instead to find just one event, bring all events which have the same amount of cues, 
		#and we decide later which one to pick
		#GeneralEvent eventFound = null;
		maxCues = 0
		eventFound = []
		for geez in self.agentGeneralEvents:
			#skip the last
			if self.agentGeneralEvents[geez].informationID == self.nextEpisodeId: 
				continue

			#for each general event, we count the cues found
			eventCues = 0
			aboutAgent = False
			#for each memory node which compounds this general event
			for node in self.agentGeneralEvents[geez].nodes:
				#if it exists, ++
				if node.information in cues:
					eventCues += 1

				#we try to avoid finding info about the agent itself or the person, if the cue is only one
				if (node.information == self.agentName or node.information == self.personName) and len(cues) == 1: 
					aboutAgent = True

			#if it is higher than the max cues, select this general event
			if eventCues > maxCues:
				if aboutAgent and eventCues == 1: 
					continue

				#reset it
				eventFound.clear()

				maxCues = eventCues
				eventFound.append(self.agentGeneralEvents[geez])
			#if has the same amount, add
			elif eventCues == maxCues:
				if aboutAgent and eventCues == 1:
					continue

				eventFound.append(self.agentGeneralEvents[geez])

		#if maxCues changed, we found an event
		#MAYBE INSTEAD OF GETTING THE MAX CUES, WE TRY TO GET EXACT CUES, SO WE DO NOT GET A RANDOM EVENT EVERYTIME, EVEN WHEN IT IS SOMETHING NOT KNOWN
		#IDEA: instead of just checking if it is above 0, it has to have, at least, 50% of the cues found
		#if maxCues >= (len(cues)/2)
		if maxCues > 0:
			theChosenOne = eventFound[0]
			#from the events found, we try to choose the one more aligned with the topic
			if len(topicSent) > 0:
				for cow in eventFound:
					for mem in cow.nodes:
						if mem.information in topicSent:
							theChosenOne = cow
							break

			#the chosen event must have more than 1 maxCues if it has person or agent
			allGood = True
			for mem in theChosenOne.nodes:
				if (mem.information == self.agentName or mem.information == self.personName) and maxCues <= 1:
					allGood = False
					break

			if allGood:
				#add the nodes back to the STM
				for mem in theChosenOne.nodes:
					self.AddToSTM(mem.informationType, mem.information, mem.weight)
				
				self.DealWithIt(theChosenOne, cues)
			else:
				#try to find the best smalltalk for this
				haa = self.FindSmallTalk(cues)

				#if not null, use it
				if haa != None:
					asToki = []
					self.SmallTalking(asToki, haa)
				#else, at least we tried
				else:
					self.Dunno()
		#else, nothing was found
		else:
			#else, see if we have some new term to learn
			#try to find the best smalltalk for this
			haa = self.FindSmallTalk(cues)

			#if not null, use it
			if haa != None:
				asToki = []
				self.SmallTalking(asToki, haa)
			#else, at least we tried
			else:
				self.Dunno()

		self.isRetrievingMemory = False

	def AddToSTM (self, informationType, information, weight = 0.1, nodeId = -1):
		#first, checks if the memory already exists
		ind = 0
		backToSTM = False

		for st in self.agentShortTermMemory:
			if self.agentShortTermMemory[st].information == information:
				ind = self.agentShortTermMemory[st].informationID

				#since it already exists, the virtual agent is remembering it. Change the activation and weight
				self.agentShortTermMemory[st].activation = self.agentShortTermMemory[st].weight = 1

				break

		#if did not find it in STM, it may be in LTM. So, lets check
		if ind == 0:
			for st in self.agentLongTermMemory:
				if self.agentLongTermMemory[st].information == information:
					ind = self.agentLongTermMemory[st].informationID

					#since it already exists, the virtual agent is remembering it. Change the activation and weight
					self.agentLongTermMemory[st].activation = self.agentLongTermMemory[st].weight = 1

					#also, since it is remembering, it should be back to STM
					backToSTM = True

					break

		#if ind is zero, we did not find the memory, so it is new. Add it
		#otherwise, if ind is not zero, but backToSTM is true, it means the memory was found in the LTM. Do not create new, but add to STM also
		if ind == 0 or (ind > 0 and backToSTM):
			#if memory is full (7 itens), forget the oldest information and store at the LTM
			if len(self.agentShortTermMemory) == 7:
				#we delete the less important memory (weight)
				less = -1
				minWeight = 1
				for mc in self.agentShortTermMemory:
					if self.agentShortTermMemory[mc].weight < minWeight:
						minWeight = self.agentShortTermMemory[mc].weight
						less = self.agentShortTermMemory[mc].informationID

				if less != -1:
					#transfer to the LTM
					self.agentLongTermMemory[self.agentShortTermMemory[less].informationID] = self.agentShortTermMemory[less]

					#delete
					self.agentShortTermMemory.remove(less)

			#add the new memory at the beggining of the memory
			#just generate new if ind == 0 
			newMemory = None
			if ind == 0:
				if nodeId > -1:
					ind = nodeId
				else:
					ind = self.GenerateEskID()

				newMemory = ESK(datetime.now(), informationType, information, ind, weight)
				self.agentShortTermMemory[ind] = newMemory
			#else, it already exists in the LTM or in the STM.
			else:
				#if backToSTM is false, it is in the STM. So, does nothing
				#otherwise, it is in the LTM. Bring it to the STM
				if backToSTM:
					for ltm in self.agentLongTermMemory:
						if self.agentLongTermMemory[ltm].informationID == ind:
							newMemory = self.agentLongTermMemory[ltm]
							newMemory.memoryTime = datetime.now()
							break

					self.agentShortTermMemory[ind] = newMemory

		return ind

	#deal with the retrieved memory
	def DealWithIt(self, retrieved, tokens):
		responseText = ""

		#by default, we get the episode itself
		responseText += retrieved.information;

		#if it has "name", the name of the person was asked. Answer accordingly
		if "name" in tokens:
			if self.agentName in tokens:
				responseText = "My name is " + self.agentName
			elif self.personName in tokens:
				responseText = "Your name is " + self.personName

			self.SpeakYouFool(responseText)
			return

		#some things we can try to infer, like Icebreakers
		#lets divide the nodes by the type
		person = []
		location = []
		time = []
		activity = []
		emotion = []
		imagery = []
		objects = []

		for mem in retrieved.nodes:
			if mem.informationType == "Person": 
				person.append(mem)
			if mem.informationType == "Location": 
				location.append(mem)
			if mem.informationType == "Time": 
				time.append(mem)
			if mem.informationType == "Activity": 
				activity.append(mem)
			if mem.informationType == "Emotion": 
				emotion.append(mem)
			if mem.informationType == "Imagery": 
				imagery.append(mem)
			if mem.informationType == "Object": 
				objects.append(mem)

		#if we have activity
		if len(activity) > 0:
			for mem in activity:
				#if it is "born", we get the age
				if mem.information == "born" and len(time) > 0:
					#memTime = datetime.strptime(time[0].information, "%d/%m/%Y %I:%M:%S %p")
					memTime = int(time[0].information)
					responseText = str(datetime.now().year - memTime) +" years old"
					break
				#if it is meet, we also need to show the date, not the normal day (not "today", for example)
				elif mem.information == "meet" and len(time) > 0:
					responseText = "Yeah, we met at " + time[0].information
					break
				
		#get emotion as well, if any
		memEmotion = ""
		if len(emotion) > 0:
			memEmotion = emotion[0].information

		#update PAD based on event polarity, if not bored
		if not self.isBored:
			self.UpdatePadEmotion(retrieved.polarity, memEmotion)

		self.SpeakYouFool(responseText)

	def GenerateEskID(self):
		self.nextEskId += 1
		return self.nextEskId

	def GenerateEpisodeID(self):
		self.nextEpisodeId += 1
		return self.nextEpisodeId

	#update PAD and check emotion
	def UpdatePadEmotion(self, polarity, memEmotion = ""):
		self.pad.UpdatePAD(polarity, memEmotion)

		chosenEmo = self.FindPADEmotion()

		self.SetEmotion(chosenEmo.lower())

	#dunno
	def Dunno(self):
		self.SpeakYouFool("Sorry, i do not know.")

	#meet someone new
	def MeetNewPeople(self):
		greetingText = "Hello stranger! May i know your name?"
		self.SpeakYouFool(greetingText)

		#need to wait for the answer
		self.isGettingInformation = False
		self.isKnowingNewPeople = True

	#at the first time the agent founds a face, checks if it already knows it. If so, greet it
	def GreetingTraveler(self, mate):
		greetingText = "Greetings " + mate + "!"

		#back to chatbot
		self.isGettingInformation = False
		self.isKnowingNewPeople = False

		#since they know each other, lets start to break the ice!
		self.isBreakingIce = True
		self.BreakIce(greetingText)

	#breaking the ice!
	def BreakIce(self, beforeText = ""):
		self.saveNewMemoryNode = False

		#reset the idle timer
		self.idleTimer = datetime.now()

		actualIceBreaker = self.iceBreakers.FindIcebreaker(self.usingIceBreaker)
        
		#just follow the tree
		#if still not using any, get the first
		if self.usingIceBreaker == 0:
			self.usingIceBreaker = self.iceBreakers.GetChild(0).GetId()
			self.rootIceBreaker = self.iceBreakers.GetId()
		else:
			#othewise, we check if this icebreaker has children. 
			#If it has, it means it has an alternative route depending on the answer of the person
			if actualIceBreaker.QntChildren() > 0:
				#now we check which question is it
				#if it is one of the first levels, we check the polarity of the answer: if it is opposite of what was expected, we take the route
				if actualIceBreaker.GetParent().GetId() == 0:
					if (actualIceBreaker.GetPolarity() == True and self.lastPolarity < 0) or (actualIceBreaker.GetPolarity() == False and self.lastPolarity > 0):
						#down the hill
						self.usingIceBreaker = actualIceBreaker.GetChild(0).GetId()
					else:
						#otherwise, we just get next
						thisChild = actualIceBreaker.CheckWhichChild()

						#next one
						thisChild += 1

						#see if the parent has more children
						if self.iceBreakers.FindIcebreaker(self.rootIceBreaker).QntChildren() > thisChild:
							self.usingIceBreaker = self.iceBreakers.FindIcebreaker(self.rootIceBreaker).GetChild(thisChild).GetId()
						#otherwise, we are done
						else:
							self.usingIceBreaker = -1
							self.rootIceBreaker = -1
				#otherwise, just keep going
				else:
					self.usingIceBreaker = actualIceBreaker.GetChild(0).GetId()
			#Otherwise, we can just go on to the next
			else:
				thisChild = actualIceBreaker.CheckWhichChild()

				#next one
				thisChild += 1

				#see if the parent has more children
				if self.iceBreakers.FindIcebreaker(self.rootIceBreaker).QntChildren() > thisChild:
					self.usingIceBreaker = self.iceBreakers.FindIcebreaker(self.rootIceBreaker).GetChild(thisChild).GetId()
				#otherwise, we are done
				else:
					self.usingIceBreaker = -1
					self.rootIceBreaker = -1
        
		#if found some icebreaker to still use, icebreak should not be empty
		if self.usingIceBreaker > 0:
			#before we speak, we should check the memory to see if this questions was already answered before.
			target = self.iceBreakers.FindIcebreaker(self.usingIceBreaker)

			targetType = target.GetType()
			if targetType == "old":
				targetType = "born"
			if targetType == "working":
				targetType = "job"
			if targetType == "study":
				targetType = "studying"

			#so, lets try to find some general event
			fuck = None

			for geez in self.agentGeneralEvents:
				#if it exists, ding!
				if self.personName in self.agentGeneralEvents[geez].information and targetType in self.agentGeneralEvents[geez].information:
					fuck = self.agentGeneralEvents[geez]
					break

			#if found it, we change the question to reflect the previous knowledge
			#update: here, we do not make questions again. We just dont call icebreakers
			if fuck != None:
				self.BreakIce(beforeText)
				return
			#otherwise, just make the question
			else:
				self.SpeakYouFool(beforeText + target.GetQuestion())
		#else, there is no more to talk about. Stop it
		else:
			if beforeText != "":
				self.SpeakYouFool(beforeText)
			else:
				self.SpeakYouFool("Thanks! Anything else you would like to talk about?")

			self.isBreakingIce = False
