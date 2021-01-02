#time with no eye detection before we arm the system (minutes)
time_to_arm=10
#once armed, how many frames before we trigger an alert
frames_to_trigger=1
#the window in which to count the above (seconds)
trigger_window=10
fps=25
repeat_alert_minutes=1

#fiddle with these numbers to tune the system.
#Scale factor indicates how much the image is reduced at each scale
#min_neghbours is a measure of certainty
face_scale_factor=1.3
face_min_neighbours=5
eye_scale_factor=2
eye_min_neighbours=5

import configparser
from datetime import timedelta
from datetime import datetime
import cv2
import telebot 

config = configparser.ConfigParser()
config.sections()
config.read('config.ini')

rtsp_src = config['SOURCE']['uri']

token = config['TELEGRAM']['token']
groupId = config['TELEGRAM']['groupId']

time_to_arm = config['NOTIFICATIONS']['time_to_arm']
frames_to_trigger = config['NOTIFICATIONS']['frames_to_trigger']
trigger_window = config['NOTIFICATIONS']['trigger_window']
fps = config['NOTIFICATIONS']['fps']
repeat_alert_minutes = config['NOTIFICATIONS']['repeat_alert_minutes']

face_scale_factor=config['DETECTOR']['face_scale_factor']
face_min_neighbours=config['DETECTOR']['face_min_neighbours']
eye_scale_factor=config['DETECTOR']['eye_scale_factor']
eye_min_neighbours=config['DETECTOR']['eye_min_neighbours']

print(str(face_scale_factor))
exit()

def sendAlert(frame, message):
    bot = telebot.TeleBot(token)
    bot.config['api_key'] = token
    ret = bot.send_message(groupId, message)
    ret = bot.sendPhoto(groupId, (frame,'rb'))
    print(ret)


alert_backoff = timedelta(minutes=repeat_alert_minutes)
last_alert=datetime.now()-alert_backoff

spf=1/fps
frame_delay = timedelta(seconds=spf)
last_run = datetime.now()-frame_delay

cam = cv2.VideoCapture(rtsp_src)
data=[]
 
face_cascade=cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
eye_cascade=cv2.CascadeClassifier('haarcascade_eye.xml')

while True:
    now = datetime.now()

    if ((now - last_run).total_seconds()) > spf:
        ret, frame = cam.read()
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
                if (count > frames_to_trigger) and ((now - last_alert).total_seconds() > repeat_alert_minutes*60):
                    last_alert = datetime.now()
                    sendAlert(roi_orig, "Awake")

        cv2.imshow('nanoCam',frame)
    if cv2.waitKey(1)==ord('q'):
        break
cam.release()
cv2.destroyAllWindows()