from flask import Flask
from flask import render_template, Response #request, escape,
from flask import send_from_directory
import os
from PAD import PAD
import cv2
import numpy as np

# Create an instance of the Flask class that is the WSGI application.
# The first argument is the name of the application module or package,
# typically __name__ when using a single module.
app = Flask(__name__)

camera = cv2.VideoCapture(0)

pad = PAD(0.8, 0.5, 0.5)

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

if __name__ == '__main__':
    # Run the app server on localhost:4449
    app.run('localhost', 4449)
