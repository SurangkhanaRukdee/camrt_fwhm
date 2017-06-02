# -*- coding: utf-8 -*-
"""
Created on Tue May 23 12:18:33 2017

@author: Srukdee

This program is implemented to control a camera connected to the computer in realtime.
The current version is used with imaging source camera 5.6 um pixel size.
It can do some easy tasks e.g. adjust exposure time, zoom, FWHM analysis.
- Image window is the real image captured by the camera; 
  this is where you click on the image and it can measure FWHM showing in Plot window
- Plot window is used for calculating FWHM along the horizontal cut on the image
- Zoom window shows the zoom image of the clicked region; adjust Z in the code if you need larger zoom

Some important key
- x = quit and destroy all window
- z = increase exposure time by +0.05 s each time 
- c = decrease exposure time by -0.05 s each time

"""

import numpy as np
import cv2
import matplotlib.pyplot as plt

fig = plt.figure()
cap = cv2.VideoCapture(1) #0 if you use the laptop camera, also need to find a correct port that match.

ix,iy = 0,0

def draw_line(event,x,y,flags,param):
    if event == cv2.EVENT_LBUTTONDBLCLK:
        global ix,iy
        print x,y
        ix,iy = x,y

img1 = (0,0)
cv2.imshow('image',img1)
cv2.setMouseCallback('image',draw_line)
exposure=0

while(True):
    # update data
    plt.clf()

    # display camera feed
    ret,frame = cap.read()
    img1 = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) #make it grey
    
    #frame = img1.copy()
    cv2.line(frame, (ix-680,iy),(ix+680,iy),(255,0,0),1)
    cv2.imshow("image",frame)

    y = (img1[iy,:])
    #print y.shape, img1.shape
    x = np.arange(len(y))
    peak = y.max()    
    mask = y>=peak/2
    xlow = x[mask].min()
    xhigh = x[mask].max()
    pixels = xhigh-xlow
    size = pixels*5.6 #pixel size of imaging source camera is 5.6 um
    plt.title('FWHM = %d pixels corresponding to %d um'  %(pixels, size))
    
    
    line1, = plt.plot(x,y); plt.grid()
    
    ax = fig.gca()
    ax.set_xticks(np.arange(0, 680, 50))
    fig.canvas.draw() # redraw the canvas
   
    # convert canvas to image
    img = np.fromstring(fig.canvas.tostring_rgb(), dtype=np.uint8,sep='')
    img  = img.reshape(fig.canvas.get_width_height()[::-1] + (3,))
    
    # img is rgb, convert to opencv's default bgr
    img = cv2.cvtColor(img,cv2.COLOR_RGB2BGR)
    
    # display image with opencv or any operation you like
    cv2.imshow("plot",img)  
    
    # For zooming the region 200x200 pixels where was clicked
    pts1 = np.float32([[ix-100,iy-100],[ix-100,iy+100],[ix+100,iy-100],[ix+100,iy+100]])

    z = 3 #x times zoom
    pts2 = np.float32([[0,0],[0,z*200],[z*200,0],[z*200,z*200]]) #upright
    #pts2 = np.float32([[0,z*200],[0,0],[z*200,z*200],[z*200,0]]) #180 deg upsidedown   
    #pts2 = np.float32([[z*200,0],[0,0],[z*200,z*200],[0,z*200]]) #90 deg rotate right
    #pts2 = np.float32([[0,0],[z*200,0],[0,z*200],[z*200,z*200]]) #90 deg rotate left
    M = cv2.getPerspectiveTransform(pts1,pts2)
    dst = cv2.warpPerspective(img1,M,(500,500))
    # Plotting the last output in the end
    plt.subplot(131),plt.imshow(img1),plt.title('Input')
    plt.subplot(132),plt.imshow(dst),plt.title('Zoom')
    plt.subplot(133),plt.imshow(img),plt.title('FWHM %d pixels'  %pixels)

    #cv2.line(dst, (ix-680,iy),(ix+680,iy),(255,0,0),1)
    cv2.imshow("zoom",dst)     

    # set exposure time
    #cap.set(cv2.cv.CV_CAP_PROP_EXPOSURE,0.5)
    key = cv2.waitKey(1)
    if key == ord('x'):
        break
    elif key == ord('z'):
        exposure+=0.05
        cap.set(cv2.cv.CV_CAP_PROP_EXPOSURE,exposure)
        print exposure
    elif key == ord('c'):
        exposure-=0.05
        cap.set(cv2.cv.CV_CAP_PROP_EXPOSURE,exposure)
        print exposure

cap.release()
cv2.destroyAllWindows() 