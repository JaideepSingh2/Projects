import cv2
import sys
import eye_detect
import numpy

#specify number of training data images to acquire
count = 25
#specify starting index to name files (to prevent overwriting previous files)
e = 1 #starting index
#specify pathname of folder to save files 
pathname = "./user1_close"

#cascPath = sys.argv[1]
#faceCascade = cv2.CascadeClassifier(cascPath)
faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades +'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades +'haarcascade_eye.xml')

video_capture = cv2.VideoCapture(0)

estart = e
while (e <= count):
    # Capture frame-by-frame
    ret, frame = video_capture.read()

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
        flags=cv2.CASCADE_SCALE_IMAGE
    )

    # Draw a rectangle around the faces
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = frame[y:y+h, x:x+w]
        eyes = eye_cascade.detectMultiScale(roi_gray)

        e2 = 1
        for (ex,ey,ew,eh) in eyes:
            if e2 <= 2:
                cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(255,0,0),2)

                if (e <= estart + 50 -1):
                    filename = "eye" + str(e) + ".png"
                    e += 1
                    name = pathname + "/" + filename
                    cv2.imwrite(name, roi_color[ey:ey+eh, ex:ex+eh])
            e2 += 1

    # Display the resulting frame
    cv2.imshow('Video', frame)
    #cv2.imshow('image', mask)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything is done, release the capture
video_capture.release()
cv2.destroyAllWindows()
