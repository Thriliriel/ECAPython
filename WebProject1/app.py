#from http.client import responses
from time import sleep
from flask import Flask, request
from flask import render_template, Response #request, escape,
from flask import send_from_directory
import os
import cv2
from Main import Main
import sys
import random
from turbo_flask import Turbo
import threading
import time
#import numpy as np
#import asyncio

# Create an instance of the Flask class that is the WSGI application.
# The first argument is the name of the application module or package,
# typically __name__ when using a single module.
app = Flask(__name__)

# turboFlask tutorial: https://blog.miguelgrinberg.com/post/dynamically-update-your-flask-web-pages-using-turbo-flask
turbo = Turbo(app)

camera = cv2.VideoCapture(0)

mainControl = Main()

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
	awake()

	update()

	return render_template('index.html', padValue = mainControl.pad, chatLog = mainControl.chatLog)

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

def awake():
	mainControl.Awake()

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/update')
def update():
	while True:
		response = "Batata!!!"
		print(response)
		sleep(1/mainControl.fps)
		yield response
		#return response, 200, {'Content-Type': 'text/plain'}

@app.route('/chat', methods=('GET', 'POST'))
def chat():
	chatText = ""
	if request.method == 'GET':
		chatText = request.args.get('chatText')
	print(chatText)
	mainControl.SendRequestChat(chatText)
	update_load()
	return chatText

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

@app.context_processor
def inject_load():
	return {'chatLog': mainControl.chatLog}

def update_load():
	with app.app_context():
		turbo.push(turbo.replace(render_template('chat.html'), 'load'))
#def update_load():
#    with app.app_context():
#        while True:
#            time.sleep(2)
#            turbo.push(turbo.replace(render_template('chat.html'), 'load'))

#@app.before_first_request
#def before_first_request():
#    threading.Thread(target=update_load).start()

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