import numpy as np
import cv2 as cv
from datetime import datetime
from time import sleep
import Benchmarking as benchmarking
import threading
import picamera 
from picamera.array import PiRGBArray
import config

threadRunning = False
thread = None
original = None
grey = None
binary = None
canny = None
processed = None

def updateCameraValues():
    global camera

    camera.resolution = (config.load()["resolutionWidth"], config.load()["resolutionHeight"])
    camera.framerate = config.load()["framerate"]

#Initializing the pi-camera
print("Initializing camera.") 
camera = picamera.PiCamera()
updateCameraValues()

sleep(1)
print("Camera initialization done.")

def convertImageToGrayScale(image):
    return cv.cvtColor(image,cv.COLOR_BGR2GRAY)

def convertImageToBinary(image): 
    return cv.threshold(image, config.load()["contrast"], 255, cv.THRESH_BINARY)[1]

def convertImageToCanny(image):
    return cv.Canny(image,50,150)

def calculateHoughImage(image): 
    lines = cv.HoughLines(image,1, np.pi / 180, 150, None, 0, 0)
    if lines is None: 
        lines = []

    return lines

def addHoughLinesOnImage(image, lines, color):

    if len(lines) == 0: 
        return image

    for rho, theta in lines[0]:
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a * rho
        y0 = b * rho
        x1 = int(x0 + 1000*(-b))
        y1 = int(y0 + 1000*(a))
        x2 = int(x0 - 1000*(-b))
        y2 = int(y0 - 1000*(a))
        cv.line(image, (x1,y1), (x2,y2), color, 2)
    
    return image

def process():
    global original, grey, binary, canny, camera, processed

    raw_capture = PiRGBArray(camera, size=(RESOLUTION_WIDTH, RESOLUTION_HEIGHT))

    print("Image processing thread has started.")
    for frame in camera.capture_continuous(raw_capture, format="bgr", use_video_port=True):
        
        if not threadRunning: 
            break
        
        original = frame.array
        #original = cv.imread("/var/www/control-panel/capture.jpg")
        grey = convertImageToGrayScale(original)
        binary = convertImageToBinary(grey)
        canny = convertImageToCanny(binary)
        hough = calculateHoughImage(canny)
        processed = addHoughLinesOnImage(canny, hough, (0,0,255)) # Setting the processed image to hough for now.  
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
