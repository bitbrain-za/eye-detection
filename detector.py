import configparser
from datetime import timedelta
from datetime import datetime
import cv2
import telebot 

config = configparser.ConfigParser()
config.sections()
config.read('config.ini')

camera_uri = config['SOURCE']['uri']

notifications = config['NOTIFICATIONS'].getboolean('enabled')
display = config['SINK'].getboolean('enabled')

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
    bot = telebot.TeleBot(token)
    # bot.config['api_key'] = token
    ret = bot.send_message(groupId, message, parse_mode="Markdown")
    photo = open('temp.jpg', 'rb')
    bot.send_photo(groupId, photo)

alert_backoff = timedelta(minutes=repeat_alert_minutes)
last_alert=datetime.now()-alert_backoff

spf=1/fps
frame_delay = timedelta(seconds=spf)
last_run = datetime.now()-frame_delay

cam = cv2.VideoCapture(camera_uri)
data=[]
 
face_cascade=cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
eye_cascade=cv2.CascadeClassifier('haarcascade_eye.xml')

while True:
    now = datetime.now()

    if ((now - last_run).total_seconds()) > spf:
        ret, frame = cam.read()
        if ret:
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

            if display:
                cv2.imshow('nanoCam',frame)
        if cv2.waitKey(1)==ord('q'):
            break
cam.release()
cv2.destroyAllWindows()