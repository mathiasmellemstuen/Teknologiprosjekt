import numpy as np
import cv2 as cv
from datetime import datetime
from time import sleep
import Benchmarking as benchmarking
import threading
import picamera 
from picamera.array import PiRGBArray
import config
import json

threadRunning = False
thread = None
original = None
grey = None
binary = None
canny = None
processed = None

contrast = 128
def updateCameraValues():
    global camera

    camera.resolution = (config.load()["resolutionWidth"], config.load()["resolutionHeight"])
    camera.framerate = config.load()["framerate"]

#Initializing the pi-camera
print("Initializing camera.") 
camera = picamera.PiCamera()
updateCameraValues()
print("Camera initialization done.")
print("--------------------")
print("|Camera values:")
print("|Resolution width:", config.load()["resolutionWidth"])
print("|Resolution height:", config.load()["resolutionHeight"])
print("|Framerate:", config.load()["framerate"]) 
print("|Contrast:", config.load()["contrast"])
print("--------------------")
sleep(1)

def convertImageToGrayScale(image):
    return cv.cvtColor(image,cv.COLOR_BGR2GRAY)

def convertImageToBinary(image):
    global contrast
    try:
        newContrast = config.load()["contrast"]
    except json.decoder.JSONDecodeError: 
       newContrast = None

    contrast = newContrast if newContrast is not None else contrast

    return cv.threshold(image, contrast, 255, cv.THRESH_BINARY)[1]

def convertImageToCanny(image):
    return cv.Canny(image,50,150)

def calculateHoughImage(image): 
#    lines = cv.HoughLines(image,1, np.pi / 180, 150, None, 0, 0)
    lines = cv.HoughLinesP(image,1,np.pi / 180,100,100,100,10)
    if lines is None: 
        lines = []

    return lines

def addHoughLinesOnImage(image, lines, color):
    #print(image)
    #print("This is line image.") 
    #image = cv.cvtColor(image, cv.COLOR_GRAY2BGR) 
    #image = cv.line(image,(0,0),(300,300),(0,0,240),10)
    #return image
    if len(lines) == 0: 
        print("Could not add hough lines. Returning.")
        return image
    image = cv.cvtColor(image, cv.COLOR_GRAY2BGR)

    for x1,y1,x2,y2 in lines[0]:
        image = cv.line(image, (x1,y1), (x2,y2), color, 2)
#    for rho, theta in lines[0]:
#        a = np.cos(theta)
#        b = np.sin(theta)
#        x0 = a * rho
#        y0 = b * rho
#        x1 = int(x0 + 1000*(-b))
#        y1 = int(y0 + 1000*(a))
#        x2 = int(x0 - 1000*(-b))
#        y2 = int(y0 - 1000*(a))
#        print("Creating a line between x1:", x1, ", y1:",y1,", x2:",x2,", y2:",y2)
#        image = cv.cvtColor(image, cv.COLOR_GRAY2BGR)
#        image = cv.line(image, (x1,y1), (x2,y2), color, 2)

    return image

def process():
    global original, grey, binary, canny, camera, processed

    raw_capture = PiRGBArray(camera, size=(config.load()["resolutionWidth"], config.load()["resolutionHeight"]))

    print("Image processing thread has started.")
    for frame in camera.capture_continuous(raw_capture, format="bgr", use_video_port=True):
        
        original = frame.array
        #original = cv.imread("/var/www/control-panel/capture.jpg")
        grey = convertImageToGrayScale(original)
        binary = convertImageToBinary(grey)
        canny = convertImageToCanny(binary)
        hough = calculateHoughImage(canny)
        houghImage = addHoughLinesOnImage(canny, hough, (0,0,255))
        processed = houghImage  
        raw_capture.truncate(0)


def getOriginalImage():
    ret, jpeg = cv.imencode('.jpg', original)
    return jpeg.tobytes()

def getGreyImage(): 
    ret, jpeg = cv.imencode('.jpg', grey)
    return jpeg.tobytes()

def getBinaryImage(): 
    ret, jpeg = cv.imencode('.jpg', binary)
    return jpeg.tobytes()

def getProcessedImage():
    ret, jpeg = cv.imencode('.jpg', processed)
    return jpeg.tobytes()

def startImageProcessingThread(): 
    global thread, threadRunning
    threadRunning = True
    thread = threading.Thread(target = process)
    thread.start()

def stopImageProcessingThread(): 
    global thread, threadRunning
    threadRunning = False
    thread.join()
