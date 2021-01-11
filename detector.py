import configparser
from datetime import timedelta
from datetime import datetime
import cv2
import telebot 
from flask import Response
from flask import Flask
from flask import render_template
import threading
import argparse

# bufferless VideoCapture
class VideoCapture:

	def __init__(self, name):
		self.outputFrame = None
		self.lock = threading.Lock()
		self.cap = cv2.VideoCapture(name)
		self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
		t = threading.Thread(target=self._reader)
		t.daemon = True
		t.start()

	# read frames as soon as they are available, keeping only most recent one
	def _reader(self):
		while True:
			ret, frame = self.cap.read()
			if not ret:
				break
			with lock:
				self.outputFrame = frame.copy()

	def read(self):
		with lock:
			retval = self.outputFrame.copy()
		return retval

# initialize the output frame and a lock used to ensure thread-safe
# exchanges of the output frames (useful when multiple browsers/tabs
# are viewing the stream)
outputFrame = None
lock = threading.Lock()

# initialize a flask object
app = Flask(__name__)

@app.route("/")
def index():
	# return the rendered template
	return render_template("index.html")

def generate():
	# grab global references to the output frame and lock variables
	global outputFrame, lock

	# loop over frames from the output stream
	while True:
		# wait until the lock is acquired
		with lock:
			# check if the output frame is available, otherwise skip
			# the iteration of the loop
			if outputFrame is None:
				continue

			# encode the frame in JPEG format
			(flag, encodedImage) = cv2.imencode(".jpg", outputFrame)

			# ensure the frame was successfully encoded
			if not flag:
				continue

		# yield the output frame in the byte format
		yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
			bytearray(encodedImage) + b'\r\n')

@app.route("/video_feed")
def video_feed():
	# return the response generated along with the specific media
	# type (mime type)
	return Response(generate(),
		mimetype = "multipart/x-mixed-replace; boundary=frame")

def detector():
	global outputFrame, lock
	config = configparser.ConfigParser()
	config.sections()
	config.read('config.ini')
	camera_uri = config['SOURCE']['uri']

	notifications = config['NOTIFICATIONS'].getboolean('enabled')
	display = config['SINK'].getboolean('enabled')
	keep_frame = config['SINK'].getboolean('keep_frame')
	if keep_frame:
		output_location = config['SINK']['keep_frame_location']

	token = config['TELEGRAM']['token']
	groupId = config['TELEGRAM']['groupId']

	frames_to_trigger = int(config['NOTIFICATIONS']['frames_to_trigger'])
	trigger_window = int(config['NOTIFICATIONS']['trigger_window'])
	fps = int(config['NOTIFICATIONS']['fps'])
	repeat_alert_minutes = int(config['NOTIFICATIONS']['repeat_alert_minutes'])

	face_scale_factor=float(config['DETECTOR']['face_scale_factor'])
	face_min_neighbours=int(config['DETECTOR']['face_min_neighbours'])
	eye_scale_factor=float(config['DETECTOR']['eye_scale_factor'])
	eye_min_neighbours=int(config['DETECTOR']['eye_min_neighbours'])

	def sendAlert(frame, message):
		cv2.imwrite("temp.jpg", frame)
		try:
			bot = telebot.TeleBot(token)
			# bot.config['api_key'] = token
			ret = bot.send_message(groupId, message, parse_mode="Markdown")
			photo = open('temp.jpg', 'rb')
			bot.send_photo(groupId, photo)
		except:
			print("Error sending notification")

	alert_backoff = timedelta(minutes=repeat_alert_minutes)
	last_alert=datetime.now()-alert_backoff

	spf=1/fps
	frame_delay = timedelta(seconds=spf)
	last_run = datetime.now()-frame_delay

	cam = VideoCapture(camera_uri)
	data=[]
	
	face_cascade=cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
	eye_cascade=cv2.CascadeClassifier('haarcascade_eye.xml')

	while True:
		now = datetime.now()

		if ((now - last_run).total_seconds()) > spf:
			frame = cam.read()
			if True:
				monochrome=cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
				last_run = now
				faces=face_cascade.detectMultiScale(monochrome, face_scale_factor, face_min_neighbours)
				for (x,y,w,h) in faces:
					cv2.rectangle(frame, (x, y) , (x+w, y+h), (0,0,255), 2)
					roi=monochrome[y:y+h, x:x+h]
					roi_orig=frame[y:y+h, x:x+h]
					eyes=eye_cascade.detectMultiScale(roi, eye_scale_factor, eye_min_neighbours)
					for(xE, yE, wE, hE) in eyes:
						cv2.rectangle(roi_orig, (xE, yE) , (xE+wE, yE+hE), (255,0,0), 1)
					if 2 == len(eyes):
						data.append(now)
						for (timestamp) in data:
							if(now - timestamp).total_seconds() > trigger_window:
								data.remove(timestamp)
						count = len(data)
						if (count > frames_to_trigger) and ((now - last_alert).total_seconds() > repeat_alert_minutes*60) and (notifications):
							last_alert = datetime.now()
							message = "Open eyes spotted. Stream: " + camera_uri
							sendAlert(roi_orig, message)

				with lock:
					outputFrame = frame.copy()

				if display:
					cv2.imshow('nanoCam',frame)
			if cv2.waitKey(1)==ord('q'):
				break
	cam.release()
	cv2.destroyAllWindows()

if __name__ == '__main__':
	config = configparser.ConfigParser()
	config.sections()
	config.read('config.ini')
	ip = config['SINK']['ip']
	port = config['SINK']['port']

	t = threading.Thread(target=detector)
	t.daemon = True
	t.start()

	# start the flask app
	app.run(host=ip, port=port, debug=False, threaded=True, use_reloader=False)