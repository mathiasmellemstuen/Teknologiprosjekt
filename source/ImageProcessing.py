import numpy as np
import cv2 as cv
from datetime import datetime
from time import sleep
import Benchmarking as benchmarking
import threading
#import picamera 
#from picamera.array import PiRGBArray
import config
import json
import math

threadRunning = False
thread = None
original = None
grey = None
binary = None
canny = None
processed = None

contrast = 128
crossDirection = "forward" # forward|left|right|random
step = 10

def updateCameraValues():
    global camera

    camera.resolution = (config.load()["resolutionWidth"], config.load()["resolutionHeight"])
    camera.framerate = config.load()["framerate"]

#Initializing the pi-camera
#print("Initializing camera.") 
#camera = picamera.PiCamera()
#updateCameraValues()
#print("Camera initialization done.")
#print("--------------------")
#print("|Camera values:")
#print("|Resolution width:", config.load()["resolutionWidth"])
#print("|Resolution height:", config.load()["resolutionHeight"])
#print("|Framerate:", config.load()["framerate"]) 
#print("|Contrast:", config.load()["contrast"])
#print("--------------------")
#sleep(1)

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
    c = config.load()
    return cv.Canny(image,c["cannyTreshold1"],c["cannyTreshold2"], apertureSize=3)

def addDilationToImage(image): 
    return cv.dilate(image,np.ones((3,3),np.uint8))

def calculateHoughImage(image): 
    c = config.load()
    
    lines = cv.HoughLinesP(image,c["houghlinesRho"],c["houghlinesTheta"],c["houghlinesTreshold"],minLineLength=c["houghlinesMinLineLength"],maxLineGap=c["houghlinesMaxLineGap"])
    if lines is None: 
        lines = []

    return lines

def calculateLineAngle(x1,y1,x2,y2):
    dx = x2 - x1
    dy = y2 - y1
    return math.atan2(dy,dx)

def calculateNodes(houghLines, width, height): 
    global crossDirection, step
    nodes = []
    crossDirection = config.load()["crossDirection"]
    step = config.load()["step"]
    nodeMargin = config.load()["nodeMargin"]

    for line in houghLines: 
        for x1,y1,x2,y2 in line: 
            lineAngle = abs(calculateLineAngle(x1,y1,x2,y2))
            #print(lineAngle) 
            if (lineAngle >= (math.pi / 4) and lineAngle <= ((3*math.pi)/4)) or (lineAngle >= math.pi + (math.pi/4) and lineAngle <= ((2*math.pi) - (math.pi/4))):
                # Vertical search
                #print("Inside angles.")
                for y in range(y1,y2,step):
                    for line2 in houghLines:
                        if line2 is not line:
                            for a1,b1,a2,b2 in line2: 
                                if y >= b1 and y <= b2 and y >= y1 and y <= y2:
                                    x = (x2 - x1) + x1 if x2 >= x1 else (x1 - x2) + x2
                                    a = (a2 - a1) + a1 if a2 >= a1 else (a1 - a2) + a2
                                    
                                    if abs(x - a) < nodeMargin:
                                        continue

                                    xPos = ((a - x) / 2) + x if a >= x else ((x - a) / 2) + a
                                   # print("x:",x,"a:",a,"xPos:",xPos, "with angle:",lineAngle)  
                                    element = {"x":xPos, "y": y}

                                    if element not in nodes:
                                        nodes.append(element)
                                   
            else:
                # Horizontal search
                pass                       

    return nodes

def addNodesOnImage(image, nodes, color):
    if nodes is not None: 
        for node in nodes: 
            if node is None: 
                continue
            image = cv.circle(image,(int(node["x"]),int(node["y"])),5,(0,255,0),-1)
    image = cv.putText(image,"Nodes: "+str(len(nodes)),(10,20),cv.FONT_HERSHEY_COMPLEX,1,(57,255,20),1,cv.LINE_AA) 
    return image

def addHoughLinesOnImage(image, lines, color):

    if len(lines) == 0:  
        return image

    image = cv.cvtColor(image, cv.COLOR_GRAY2BGR) 
    for line in lines:
        for x1,y1,x2,y2 in line:
            cv.line(image, (x1,y1), (x2,y2), color, config.load()["houghlinesRedLinePixels"])
    image = cv.putText(image, "Lines: " + str(len(lines)),(10,60),cv.FONT_HERSHEY_COMPLEX,1,(57,255,20),1,cv.LINE_AA)
    
    return image

def process():
    global original, grey, binary, canny, camera, processed, threadRunning

    raw_capture = PiRGBArray(camera, size=(config.load()["resolutionWidth"], config.load()["resolutionHeight"]))

    for frame in camera.capture_continuous(raw_capture, format="bgr", use_video_port=True):
        #Breaking out of the loop if we want to stop the thread.  
        if threadRunning is False: 
            break

        #Doing greyscaling, binary and canny calculations
        original = frame.array
        grey = convertImageToGrayScale(original)
        binary = convertImageToBinary(grey)
        canny = convertImageToCanny(binary)
        #canny = addDilationToImage(canny)

        #Adding houghlines
        hough = calculateHoughImage(canny)
        processed = addHoughLinesOnImage(canny, hough, (0,0,255))
       
        #Calculating and adding nodes
        width, height = camera.resolution
        nodes = calculateNodes(hough, width, height) 
        processed = addNodesOnImage(processed,nodes,(0,255,0))
         
        #Truncating before next loop
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

def start(): 
    global thread, threadRunning
    threadRunning = True
    thread = threading.Thread(target = process)
    thread.start()

def stop(): 
    global thread, threadRunning
    print("Stopping the image processing thread.")
    threadRunning = False
    thread.join()



originalImage = cv.imread("road.png")
grey = convertImageToGrayScale(originalImage)
binary = convertImageToBinary(grey)
canny = convertImageToCanny(binary)

contours, hierarchy = cv.findContours(binary, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

#processed = cv.drawContours(originalImage, contours, -1, (0,255,0),2)

list1 = []

h, w, c = originalImage.shape

for i in contours:
    for j in i:
        list1.append(i[0].tolist()[0])

ratio = 30

def calculateDistanceBetweenTwoPoints(x1,y1,x2,y2):
    return math.sqrt(math.pow(x2-x1,2) + math.pow(y2-y1,2))

print(list1)
print("List 1 length:", len(list1))

#Removing duplicates
s = []
for i in list1: 
    if i not in s: 
            s.append(i)

list1 = s
print("List length after deletion:", len(list1))

def deleteNearbyNodes(nodes): 
    i = 0
    while i < len(nodes): 
        j = 0
        while j < len(nodes):
            
            if i == j or not i < len(nodes):
                j+=1
                continue
            print(i, "and",len(nodes))
            distance = calculateDistanceBetweenTwoPoints(nodes[i][0],nodes[i][1],nodes[j][0],nodes[j][1])
            
            if distance < ratio:
                del nodes[j]
            j+=1
        i+=1
    return nodes

list1 = deleteNearbyNodes(list1)
print("List length after deletion nr.2:", len(list1))

for node in list1: 
    if node[0] <= w and node[1] <= h:
        print(originalImage[node[0],node[1]])
#roadNodeList = []
#step = 20
#for y in range(step,h,step):
#    n = []
#    for node in list1:
#        if node[1] >= y - step and node[1] <= y:
#            n.append(node)
#
#    if len(n) == 0:
#        continue
#    
#    averageX = 0
#    averageY = 0
#    i = 0
#    for node in n: 
#        averageX += node[0]
#        averageY += node[1]
#        i+=1
#
#    averageX = averageX / i
#    averageY = averageY / i
#
#    roadNodeList.append([int(averageX),int(averageY)])
#
#lastNode = None
#for position in roadNodeList: 
#    originalImage = cv.circle(originalImage,(position[0],position[1]),5,(128,0,255),-1)
#    if lastNode != None: 
#        originalImage = cv.line(originalImage,(position[0],position[1]),(lastNode[0],lastNode[1]),(0,0,255),2)
#
#    lastNode = position
for position in list1: 
    originalImage = cv.circle(originalImage,(position[0],position[1]),5,(0,0,255),-1)

#for position in contours[0]:
#    originalImage = cv.circle(originalImage,(position[0][0],position[0][1]),5,(255,0,0),-1)
#canny = addDilationToImage(canny)

#Adding houghlines
#hough = calculateHoughImage(canny)
#processed = addHoughLinesOnImage(canny, hough, (0,0,255))

#Calculating and adding nodes
#width, height = camera.resolution
#nodes = calculateNodes(hough, width, height) 
#processed = addNodesOnImage(processed,nodes,(0,255,0))
print(cv.imwrite("processed.jpg",originalImage))

#{
#        "nodes": [
#            {
#                "x":0,
#                "y":0
#            }
#        ]
#        "width":500,
#        "height":500
#}
