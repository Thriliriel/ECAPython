from PAD import PAD
from Topic import Topic
from Dialog import Dialog
import random
from datetime import datetime

class Main(object):
	#attributes
	#PAD
	pad = PAD(0.8, 0.5, 0.5)
	#FPS for update
	fps = 1
	#list of topics
	topics = []
	#list of topics (do not change)
	topicsFinal = []
	#current topic
	currentTopic = None
	#list with all dialogs/topics in memory
	dialogsInMemory = []
	dialogsAnswersInMemory = []
	#list with dialogs already used
	dialogsUsed = []
	#Dictionary<string, List<Tuple<string, double>>> 
	keywordsDataset = {}
	#name of the user
	personName = ""
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

	def Awake(self):

		#random agent
		rnd = random.randrange(10)
		if rnd % 2 == 0: 
			self.agentName = "Arthur"
		else: 
			self.agentName = "Bella"
			
		#if Arthur is in chat mode, we can deactivate all graphical stuff
		if self.chatMode:
			#mariano.SetActive(false);
			#belinha.SetActive(false);
			#cam.SetActive(false);
			#sleepButton.SetActive(false);
			#voiceButton.SetActive(false);
			#emotionText.SetActive(false);
			#GameObject.Find("Chat").GetComponent<RectTransform>().sizeDelta = new Vector2(700, 450);
			#GameObject.Find("Chat").GetComponent<RectTransform>().anchoredPosition = new Vector3(15, 50, 0);
			#inputText.GetComponent<RectTransform>().sizeDelta = new Vector2(620, 50);
			#inputText.GetComponent<RectTransform>().anchoredPosition = new Vector3(15, 0, 0);
			#GameObject.Find("Go").GetComponent<RectTransform>().sizeDelta = new Vector2(80, 50);
			#GameObject.Find("Go").GetComponent<RectTransform>().anchoredPosition = new Vector3(640, 0, 0);
			self.canSpeak = False
		#otherwise, is it Arthur or Bella?
		#else
		#{
		#	if(agentName == "Arthur")
		#	{
		#		mariano.SetActive(true);
		#		belinha.SetActive(false);
		#	}else if (agentName == "Bella")
		#	{
		#		mariano.SetActive(false);
		#		belinha.SetActive(true);
		#		belinha.transform.Find("EyeCTRLBella").GetComponent<EyeCTRLBella>().enabled = true;
		#	}
		#}		

		#webServicePath = "http:#localhost:8080/";

		#WITHOUT ICEBREAKERS
		#set the ice breakers
		#rootIceBreaker = usingIceBreaker = -1;
		##first element is just the pointer to the root questions
		#iceBreakers = new IceBreakingTreeClass(0, "root", "", false);
		#usingIceBreaker = 0;

		##load icebreakers and answers from the file
		#LoadIceBreakersAndStuff();

		#set the small talks
		self.LoadKeywords()
		self.LoadSTs()

		for tg in self.topics:
			self.topicsFinal.append(tg)

		#load small talks from the memory
		self.LoadMemoryDialogs()

		#PickTopic();

		##hide zzz and stuff
		#zzz.SetActive(false);
		#thinkingBalloon.SetActive(false);
		#timerObject.SetActive(false);
		#randomImage.SetActive(false);
		#riTarget.SetActive(false);

		##foundNames = new List<string>();
		#foundEmotions = new List<string>();
		#peopleGreeted = new List<string>();
		#agentShortTermMemory = new Dictionary<int, MemoryClass>();
		#agentLongTermMemory = new Dictionary<int, MemoryClass>();
		#agentGeneralEvents = new Dictionary<int, GeneralEvent>();
		#memorySpan = new TimeSpan(0, 0, 15);

		##if UNITY_EDITOR_WIN || UNITY_STANDALONE_WIN || UNITY_EDITOR_OSX || UNITY_STANDALONE_OSX || UNITY_XBOXONE
		##start the prolog
		##prolog = new PrologEngine(persistentCommandHistory: false);
		##prologStatements = new Dictionary<string, int>();
		##endif

		##what we have on textLTM, load into auxiliary LTM
		#LoadEpisodicMemory();

		##after loading the memory, we update it depending on if it is Arthur or Bella
		#if(agentName == "Arthur" && agentLongTermMemory[1].information == "Bella")
		#{
		#	agentLongTermMemory[1].information = "Arthur";
		#	agentLongTermMemory[2].information = "AutobiographicalStorage/Images/Arthur.png";
		#} else if (agentName == "Bella" && agentLongTermMemory[1].information == "Arthur")
		#{
		#	agentLongTermMemory[1].information = "Bella";
		#	agentLongTermMemory[2].information = "AutobiographicalStorage/Images/Bella.png";
		#}

		##if UNITY_EDITOR_WIN || UNITY_STANDALONE_WIN || UNITY_EDITOR_OSX || UNITY_STANDALONE_OSX || UNITY_XBOXONE
		##create the facts from the memory
		#CreateFactsFromMemory();
		##endif

		##read the next ID from the file
		##first line: ESK Ids. Second line: Episode Ids
		#nextEpisodeId = PlayerPrefs.GetInt("nextIdEvent");
		#nextEskId = PlayerPrefs.GetInt("nextIdMemory");
		##if UNITY_EDITOR_WIN || UNITY_STANDALONE_WIN || UNITY_EDITOR_OSX || UNITY_STANDALONE_OSX || UNITY_XBOXONE
		##load prolog beliefs
		#LoadBeliefs();
		##endif

		##also, see if this person already exists in memory, in the case of chat mode. If it does not, we need to add.
		#if (chatMode)
		#{
		#	bool yup = false;
		#	foreach(KeyValuePair<int, MemoryClass> ltm in agentLongTermMemory)
		#	{
		#		if(ltm.Value.information == personName)
		#		{
		#			yup = true;
		#			break;
		#		}
		#	}

		#	if (!yup)
		#	{
		#		int thisID = AddToSTM("Person", personName, 0.9f);
		#		personId = thisID;
		#		List<int> connectNodes = new List<int>();
		#		connectNodes.Add(1);
		#		connectNodes.Add(thisID);
		#		#since it is chat mode, no image
		#		#thisID = AddToSTM("Imagery", "AutobiographicalStorage/Images/" + namePerson + ".png", 0.9f);
		#		#connectNodes.Add(thisID);
		#		connectNodes.Add(11);

		#		#add this date as well
		#		string thisYear = System.DateTime.Now.ToString("yyyy-MM-dd");
		#		thisID = AddToSTM("Time", thisYear, 0.9f);
		#		connectNodes.Add(thisID);
		#		AddGeneralEvent("I met " + personName + " today", connectNodes, "person");
		#	}
		#}

		##word2vec stuff (heavy stuff, just use if chosen)
		#/*if (useW2V)
		#{
		#	w2v = new Word2vecClass();
		#	w2v.Start();
		#	#w2v.MostSimilar("boy");
		#}*/

		##background
		#Sprite sp = Resources.Load<Sprite>(chosenBackground);
		#backGround.GetComponent<SpriteRenderer>().sprite = sp;

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

		print (smallT)

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

			#if the topic is emotions, we pass the marioEmotion together to select the appropiate dialog
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
			digmem = self.currentTopic.GetId() + "-" + self.currentTopic.GetCurrentDialog().GetDescription() + "-" + self.currentTopic.GetCurrentDialog().GetId().ToString()
        
			if digmem not in self.dialogsUsed and self.currentTopic.GetId() != "emotions":
				self.dialogsUsed.append(digmem)
			if digmem not in self.dialogsInMemory and self.currentTopic.GetId() != "emotions":
				self.dialogsInMemory.append(digmem)
				self.SpeakYouFool(ct)
			if self.currentTopic.GetId() == "emotions":
				self.SpeakYouFool(ct)

		print(ct)

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