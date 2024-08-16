#Measure aspect ratio of the eye from an ROI image around the eye
import numpy
import cv2
import math

#return mask of pixels that correspond to pupils of eye
def pupil_mask(roi):
    #perform histogram equalization on the region of interest
    roi_eq = cv2.equalizeHist(roi)
    #perform thresholding on eyes
    T = 255 * 0.06
    eye_mask = numpy.zeros((len(roi_eq),len(roi_eq[0])))
    for j in range(0,len(roi_eq)):
        for i in range(0,len(roi_eq[0])):
            if roi_eq[j,i] < T:
                eye_mask[j,i] = 1

    #Perform morphological closing operation
    #kernel = numpy.array([1, 1, 1, 1, 1], dtype='uint8')
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))
    eye_mask = cv2.morphologyEx(eye_mask, cv2.MORPH_CLOSE, kernel)
    
    
    return eye_mask

#align Im1 to Im2 (Im2 must match imsize)
def align(Im1,Im2):
    rows,cols = Im1.shape
    imsize = 14 #14 corresponds to 30x30 image
    #determine central pixel at ypos, xpos around which to crop Im1
    ypos = math.floor(cols/2)
    xpos = math.floor(rows/2)
    #best alignment parameters
    best_dx = 0
    best_dy = 0
    best_mse = float("inf")

    #increments for course align (use 2 and 1)
    jumps = numpy.array([2,1])
    for delta in jumps:
        for dx in range(-delta+best_dx,delta+best_dx,delta):
            for dy in range(-delta+best_dy,delta+best_dy,delta):
                #transform Im1 according to dx, dy
                M = numpy.array([(1,0,dx),(0,1,dy)],dtype='float32')
                frameTform = cv2.warpAffine(Im1,M,(cols,rows))
                #Crop frametform 
                frameTform = frameTform[ypos-(imsize+1):ypos+(imsize+1), \
                                         xpos-(imsize+1):xpos+(imsize+1)]
                #Calculate MSE between Im1 and Im2
                difference = frameTform - Im2
                difference_squared = numpy.multiply(difference,difference)
                MSE = numpy.sum(numpy.sum(difference_squared)) / ((imsize+1)**2)
                #Remember lowest MSE
                if (MSE < best_mse):
                    best_mse = MSE
                    best_dx = dx
                    best_dy = dy
                    
    #align image using dxbest and dybest
    M = numpy.array([(1,0,best_dx),(0,1,best_dy)],dtype='float32')
    aligned_Im = cv2.warpAffine(Im1,M,(cols,rows))            
    #crop image 
    aligned_Im = aligned_Im[ypos-(imsize+1):ypos+(imsize+1), \
                              xpos-(imsize+1):xpos+(imsize+1)]
    return aligned_Im
    
    
    
    

