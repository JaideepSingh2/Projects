import cv2
import sys
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from freq_peak import *
import collections
import code
import matplotlib
from sklearn.decomposition import FastICA


#mat = np.load('ica_matrix.npy')

faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades +'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades +'haarcascade_eye.xml')

if len(sys.argv) == 1:
    video_capture = cv2.VideoCapture(0)
    fps = 30
else:
    video_capture = cv2.VideoCapture(sys.argv[1])
    fps = video_capture.get(cv2.CAP_PROP_FPS)

samp = int(10*fps)
samp2 = 10
cntr = 0
cntr2 = 0
cntr3 = 0

r = np.zeros(samp)
g = np.zeros(samp)
b = np.zeros(samp)

X = np.zeros(samp2)
Y = np.zeros(samp2)
sig_chrom = []#np.zeros(samp)

fs = fps
lowcut = 0.7
highcut = 2.5
nyq = 0.5*fs
low = lowcut / nyq
high = highcut / nyq

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
            #put ica stuff here

            r_norm = (r-np.mean(r))/np.std(r)
            g_norm = (g-np.mean(g))/np.std(g)
            b_norm = (b-np.mean(b))/np.std(b)

            C = np.vstack((r_norm,g_norm,b_norm))
            ica = FastICA(max_iter=1000)
            W = ica.fit_transform(C.T)
            sig1 = W[:,0]
            sig2 = W[:,1]
            sig3 = W[:,2]

            p1,hb1 = freq_peak(sig1,fps)
            p2,hb2 = freq_peak(sig2,fps)
            p3,hb3 = freq_peak(sig3,fps)
            peaks = np.array([p1,p2,p3])
            
            print(peaks)
            print(np.array([hb1,hb2,hb3]))

            w = ica.components_
            np.save('ica_matrix',w)
            np.save('red',r)
            np.save('blue',b)
            np.save('green',g)
            np.save('red_norm',r_norm)
            np.save('blue_norm',b_norm)
            np.save('green_norm',g_norm)
            np.save('sig1',sig1)
            np.save('sig2',sig2)
            np.save('sig3',sig3)
            cntr = cntr+1
            
    if cntr > samp:
        break
        '''
        eyes = eye_cascade.detectMultiScale(roi_gray)
        for (ex,ey,ew,eh) in eyes:
            cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(255,0,0),2)
        '''    

    # Display the resulting frame
    cv2.imshow('Video', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything is done, release the capture
video_capture.release()
cv2.destroyAllWindows()

plt.plot(sig1)
plt.show()
plt.plot(sig2)
plt.show()
plt.plot(sig3)
plt.show()
