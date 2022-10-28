from http.client import responses
from time import sleep
from flask import Flask
from flask import render_template, Response #request, escape,
from flask import send_from_directory
import os
from PAD import PAD
import cv2
from Topic import Topic
from Dialog import Dialog
#import numpy as np
#import asyncio

# Create an instance of the Flask class that is the WSGI application.
# The first argument is the name of the application module or package,
# typically __name__ when using a single module.
app = Flask(__name__)

camera = cv2.VideoCapture(0)

#variables
pad = PAD(0.8, 0.5, 0.5)
fps = 30
topics = []
#Dictionary<string, List<Tuple<string, double>>> 
keywordsDataset = {}

#favicon
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

# Flask route decorators map / and /hello to the hello function.
# To add other resources, create functions that generate the page contents
# and add decorators to define the appropriate resource locators for them.

@app.route('/')
def hello():
	#example getting GET parameter
	#celsius = str(escape(request.args.get("celsius", "")))

	#just testing
	#pad = PAD(0.8, 0.5, 0.5)
	#i = 0
	#while i < 100:
	#	pad.IncreaseBoredom(0.5, 0.8, 0.5)
	#	print(str(pad.boredom))
	#	i += 1

	gen_pad()

	return render_template('index.html', padValue = pad)

    # Render the page
    #return "Hello Python!"
	#return (
 #       """<form action="" method="get">
 #               Celsius temperature: <input type="text" name="celsius">
 #               <input type="submit" value="Convert to Fahrenheit">
 #           </form>"""
 #       + "Fahrenheit: "
 #       + fahrenheit + "\n"
 #   )

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/update')
def update():
	loadSTs()

	response = "Batata!!!"
	return response, 200, {'Content-Type': 'text/plain'}

	while True:
		response = "Batata!!!"
		print(response)
		sleep(1/fps)
		#return response, 200, {'Content-Type': 'text/plain'}

def gen_pad():
	while True:
		pad.IncreaseBoredom(0.5, 0.8, 0.5)
		print(pad.boredom)
		yield(pad.boredom)

def gen_frames():  
    while True:
        success, frame = camera.read()  # read the camera frame
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result

#async def update():
#	while True:
#		print("\n HELLO WORLD \n")
#		await asyncio.sleep(1)

#async def update2():
#	while True:
#		print("\n AAAA \n")
#		await asyncio.sleep(0.5)

#async def startWebServer():
#	# Run the app server on localhost:4449
#	app.run('localhost', 4449)

#	#await asyncio.sleep(0.1)

#async def gathering():
#	await asyncio.gather(update(), startWebServer())

def loadKeywords():
	batata = 1
	#string[] keyWords = PlayerPrefs.GetString("keywords").Split('-'); topics = new List<Topic>();
	#keywordsDataset = new Dictionary<string, List<Tuple<string, double>>>(); // node_id [(word, weight) ..]
	#foreach (string kw in keyWords)
	#{
	#	if (kw == "" || kw == null) continue;
	#	string line = kw.Trim();
	#	string[] data = line.Split(' ');

	#	string nodeId = data[0].Trim();
	#	if (!keywordsDataset.ContainsKey(nodeId))
	#	{
	#		keywordsDataset[nodeId] = new List<Tuple<string, double>>();
	#	}
	#	keywordsDataset[nodeId].Add(new Tuple<string, double>(data[1].Trim(), double.Parse(data[2].Trim())));


def loadSTs():
	fl = open("smallTalk.txt")
	smallT = fl.read().split('\n')
	fl.close()

	topics = []
	currentTopic = None
	currentDialog = None

	dialogIds = []

	for line in smallT:
		line = line.strip()

		command = line[0]

		#new topic
		if command == '$':
			currentTopic = Topic(line[2:len(line)])
			topics.Add(currentTopic);
		elif command == '[': #new dialog
			currentDialog = Dialog(line[2:len(line)])
		elif command == '#': #dialog
			currentDialog = Dialog(line[2:len(line)])

			#id, sentence, polarity, isLeaf, father id, memory edge, memory node value..
			data = line.split(';')
			nodeId = data[0].strip()
			fatherId = data[2].strip()

			if nodeId in dialogIds:
				print("PARSER ERROR: Node id already used (must be unique!): " + nodeId)
				return

			currentDialog.AddNode(nodeId, data[1].Trim(), fatherId)
			dialogIds.Add(nodeId)

			if fatherId == "-1": 
				continue #raiz não tem pai para inserir keywords !!
			
			try:
				lst = keywordsDataset[nodeId]
				currentDialog.AddKeywords(nodeId, lst, fatherId)
			except:
				print("PARSER ERROR: Node id not found: " + nodeId)
				return
		#close dialog (insert on topic)
		elif command == ']':
			currentTopic.InsertDialog(currentDialog.GetDescription(), currentDialog)

	keywordsDataset.clear(0)


if __name__ == '__main__':
	#update
	#loop = asyncio.get_event_loop()
	#asyncio.ensure_future(update())
	#loop.run_forever()
	#loop = asyncio.get_event_loop()
	#loop.run_until_complete(gathering())
	#loop.close()
	
	# Run the app server on localhost:4449
	app.run('localhost', 4449)