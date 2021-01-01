import cv2

cam = cv2.VideoCapture("rtsp://192.168.1.68:554/live/0/SUB")
 
face_cascade=cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
eye_cascade=cv2.CascadeClassifier('haarcascade_eye.xml')

while True:
    ret, frame = cam.read()
    monochrome=cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces=face_cascade.detectMultiScale(monochrome, 1.3, 5)
    for (x,y,w,h) in faces:
        cv2.rectangle(frame, (x, y) , (x+w, y+h), (0,0,255), 2)
        roi=monochrome[y:y+h, x:x+h]
        roi_orig=frame[y:y+h, x:x+h]
        eyes=eye_cascade.detectMultiScale(roi, 2, 5)
        for(xE, yE, wE, hE) in eyes:
            cv2.rectangle(roi_orig, (xE, yE) , (xE+wE, yE+hE), (255,0,0), 1)

    cv2.imshow('nanoCam',frame)
    if cv2.waitKey(1)==ord('q'):
        break
cam.release()
cv2.destroyAllWindows()