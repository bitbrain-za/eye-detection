rtsp_src="rtsp://192.168.1.68:554/live/0/SUB"
#time with no eye detection before we arm the system (minutes)
time_to_arm=10
#once armed, how many frames before we trigger an alert
frames_to_trigger=1
#the window in which to count the above (seconds)
trigger_window=10
fps=25

#fiddle with these numbers to tune the system.
#Scale factor indicates how much the image is reduced at each scale
#min_neghbours is a measure of certainty
face_scale_factor=1.3
face_min_neighbours=5
eye_scale_factor=2
eye_min_neighbours=5

from datetime import datetime
import cv2

last_run = datetime.now()
cam = cv2.VideoCapture(rtsp_src)
data=[]
spf=1/fps
 
face_cascade=cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
eye_cascade=cv2.CascadeClassifier('haarcascade_eye.xml')

while True:
    ret, frame = cam.read()
    monochrome=cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    now = datetime.now()

    if ((now - last_run).total_seconds()) > spf:
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
                if count > frames_to_trigger:
                    #notify

    cv2.imshow('nanoCam',frame)
    if cv2.waitKey(1)==ord('q'):
        break
cam.release()
cv2.destroyAllWindows()