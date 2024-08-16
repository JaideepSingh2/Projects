import cv2
import sys
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from freq_peak import *
import collections
import code
import matplotlib
import eye_detect
import math
import time

#Set display parameters for image text
font                   = cv2.FONT_HERSHEY_SIMPLEX
bottomLeftCornerOfText = (50,100)
bottomLeftCornerOfText2 = (50,200)
bottomRightCornerOfText = (50,300)
bottomRightCornerOfText2 = (50,400)
fontScale              = 1
fontScale2             = 0.5
fontColor              = (255,255,255)
lineType               = 2

# Get eigeneye and meaneye
# Pick one of the following:
# my_data = np.genfromtxt('./eye_training_data/user1_eyes.csv', delimiter=',')
# my_data = np.genfromtxt('./eye_training_data/user1and2_eyes.csv', delimiter=',')
my_data = np.genfromtxt('./eye_training_data/user3_eyes.csv', delimiter=',')

eigeneye = my_data[0:30,:]
meaneye = my_data[31:,:]

#Set initial eye status parameters
recent_status = np.array([0,0,0,0])
start = 0
end = 0

#
mat = np.load('ica_matrix.npy')

faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades +'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades +'haarcascade_eye.xml')

if len(sys.argv) == 1:
    video_capture = cv2.VideoCapture(0)
else:
    video_capture = cv2.VideoCapture(sys.argv[1])

fps = video_capture.get(cv2.CAP_PROP_FPS)
if fps == 0.0:
    fps = 30.0 # default to 30 fps

samp = int(5*fps)
samp2 = 10
cntr = 0
cntr2 = 0
cntr3 = 0

r = np.zeros(samp)
g = np.zeros(samp)
b = np.zeros(samp)

X = np.zeros(samp2)
Y = np.zeros(samp2)
sig_chrom = []

hb_chrom_reserve = np.zeros(samp)
hb_ica_reserve = np.zeros(samp)

fs = fps
lowcut = 0.7
highcut = 2.5
nyq = 0.5*fs
low = lowcut / nyq
high = highcut / nyq

hb1 = 0
hb2 = 0

b_filt,a_filt = scipy.signal.butter(3, [low, high], btype='band')

while (video_capture.isOpened()):
    # Capture frame-by-frame
    ret, frame = video_capture.read()

    if ret is False:
        break
    
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

        right_cheek = frame[int(y+.5*h):int(y+.7*h),int(x+.15*w):int(x+.35*w)]
        left_cheek = frame[int(y+.5*h):int(y+.7*h),int(x+.65*w):int(x+.85*w)]
        cv2.rectangle(frame,(int(x+.15*w),int(y+.5*h)),(int(x+.35*w),int(y+.7*h)), (0,0,255),2)
        cv2.rectangle(frame,(int(x+.65*w),int(y+.5*h)),(int(x+.85*w),int(y+.7*h)), (0,0,255),2)
        cheeks = np.hstack((right_cheek,left_cheek))
        mean_rgb = np.mean(cheeks,axis=tuple([0,1]))
        
        if cntr < samp:
            r[cntr] = mean_rgb[0]
            g[cntr] = mean_rgb[1]
            b[cntr] = mean_rgb[2]
            cntr = cntr+1
        else:
            r = np.roll(r,-1)
            r[-1] = mean_rgb[0]
            g = np.roll(g,-1)
            g[-1] = mean_rgb[1]
            b = np.roll(b,-1)
            b[-1] = mean_rgb[2]

            r_norm = (r-np.mean(r))/np.std(r)
            g_norm = (g-np.mean(g))/np.std(g)
            b_norm = (b-np.mean(b))/np.std(b)
            
            C = np.vstack((r_norm,g_norm,b_norm))
            out = mat@C
            sig1 = out[0,:]
            sig2 = out[1,:]
            sig3 = out[2,:]
            p1,hb1 = freq_peak(sig1,fps)

            # Normalize RGB
            r_norm1 = r/np.mean(r)
            g_norm1 = g/np.mean(g)
            b_norm1 = b/np.mean(b)

            # Project into chrominance plane
            X = 3*r_norm1 - 2*g_norm1
            Y = 1.5*r_norm1 + g_norm1 - 1.5*b_norm1

            # Bandpass X and Y signals
            filtered_x = scipy.signal.lfilter(b_filt,a_filt,X)
            filtered_y = scipy.signal.lfilter(b_filt,a_filt,Y)

            # Get final signal
            alpha = np.std(filtered_x) / np.std(filtered_y)
            sig_chrom = filtered_x-alpha*filtered_y

            # Find dominant frequency
            peak_chro,hb_chrom = freq_peak(sig_chrom,fps)
            #print(hb1,hb_chrom)

            hb_chrom_reserve[cntr3] = hb_chrom
            hb_ica_reserve[cntr3] = hb1
            cntr3 = cntr3+1

            if cntr3 >= int(5*fps):
                hb1 = np.median(hb_chrom_reserve)
                hb2 = np.median(hb_ica_reserve)
                #print(np.median(hb_chrom_reserve),np.median(hb_ica_reserve))
                cntr3 = 0
        cv2.putText(frame,'CHROM HBM: {:.3f}'.format(hb1),bottomRightCornerOfText,font,\
                        fontScale,fontColor,lineType)
        cv2.putText(frame,'ICA HBM: {:.3f}'.format(hb2),bottomRightCornerOfText2,font,\
                        fontScale,fontColor,lineType)
        #eyes
        eyes = eye_cascade.detectMultiScale(roi_gray)
        status = 0 #0 = open, 1 = closed
        e2 = 1 #don't consider more than 2 "eyes" in the loop

        for (ex,ey,ew,eh) in eyes:
            if e2 <= 2:
                cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(255,0,0),2)
                eye = roi_gray[ey:ey+eh, ex:ex+ew]
                #-----------Determine if eye is open or closed----------------#
                #Image is large enough to be considered? 
                if (eye.shape[0] >= 30 and eye.shape[1] >= 30):
                    #perform histogram equalization on the region of interest
                    eye = cv2.equalizeHist(eye)
                    #Align the eye to the meaneye image
                    eye = eye_detect.align(eye,meaneye)
                    #Subtract out the mean eye 
                    eye = eye - meaneye
                    #Calculate eye projection score onto eigeneye
                    eye_projection = np.multiply(eye, eigeneye)
                    eye_score = np.sum(np.sum(eye_projection))
                    #If any eyes are closed, the status is closed
                    eye_score = eye_score / 255
                    if eye_score < 0:
                        status = 1
            e2 += 1
        #update status using correction
        recent_status = np.append(recent_status[1:],status)
        #check for multiple closed eyes in succession and correct for false negatives 
        if np.array_equal(recent_status,[1,0,1,1]) \
           or np.array_equal(recent_status,[1,0,0,1]) \
           or np.array_equal(recent_status,[1,1,0,1]):
            recent_status = [1,1,1,1]
        #display eye status 
        #if recent_status[0] == 0:
        if status == 0:
            cv2.putText(frame,'OPEN',bottomLeftCornerOfText,font,\
                        fontScale,fontColor,lineType)
            if recent_status[1] == 1: #first open eye frame (end time)
                end = time.time()
        else:
            cv2.putText(frame,'CLOSED',bottomLeftCornerOfText,font,\
                        fontScale,fontColor,lineType)
            if recent_status[1] == 0: #first closed eye frame (start time) 
                start = time.time()
    # Display blink duration
    cv2.putText(frame,'last blink duration:'+'{:.3f}'.format(end-start),bottomLeftCornerOfText2,font,\
                        fontScale2,fontColor,lineType)
    # Display the resulting frame
    cv2.imshow('Video', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything is done, release the capture
video_capture.release()
cv2.destroyAllWindows()
