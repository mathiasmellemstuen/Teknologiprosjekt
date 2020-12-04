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
import math
import random

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
    c = config.load()
    return cv.Canny(image,c["cannyTreshold1"],c["cannyTreshold2"], apertureSize=3)

def addDilationToImage(image): 
    return cv.dilate(image,np.ones((3,3),np.uint8))

def calculateHoughImage(image): 
    c = config.load()
    lines = cv.HoughLinesP(image,c["houghlinesRho"],c["houghlinesTheta"],c["houghlinesTreshold"],minLineLength=c["houghlinesMinLineLength"],maxLineGap=c["houghlinesMaxLineGap"])
    if lines is None: 
        lines = []
    
    returnLines = []
    
    for line in lines:
        returnLines.append((line[0][0].item(),line[0][1].item(),line[0][2].item(),line[0][3].item()))

    return returnLines

def calculateLineRadians(x1,y1,x2,y2):
    dx = x2 - x1
    dy = y2 - y1
    return math.atan2(dy,dx)

def convertAngle0To2Pi(a):
    return a if a >= 0.0 else (2 * math.pi) + a

def ccw(A,B,C):
    return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])

def intersect(A,B,C,D):
    return ccw(A,C,D) != ccw(B,C,D) and ccw(A,B,C) != ccw(A,B,D)

def line_intersection(line1, line2):
    xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
    ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])
    
    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = det(xdiff, ydiff)
    
    if div == 0:
        return False

    d = (det(*line1), det(*line2))
    x = det(d, xdiff) / div
    y = det(d, ydiff) / div

    return int(x),int(y)

def upAngle(angle):
    return (angle >= math.pi / 4 and angle <= (3*math.pi) / 4) or (angle >= math.pi + (math.pi / 4) and angle <= (2*math.pi) - (math.pi / 4))

def calculateNodes(lines, minDistance, maxDistance, width, height):
    
    usedLines = []
    nodes = []

    for line in lines: 
        for line2 in lines: 
            if line == line2: 
                continue

            currentLineAngle = calculateLineRadians(line[0],line[1],line[2],line[3])
            currentLineAngle = convertAngle0To2Pi(currentLineAngle)
            anotherLineAngle = calculateLineRadians(line2[0],line2[1],line2[2],line2[3])
            anotherLineAngle = convertAngle0To2Pi(anotherLineAngle)

            if upAngle(currentLineAngle) and upAngle(anotherLineAngle):
                
                inter = intersect((line[0],line[1]),(width,line[1]),(line2[0],line2[1]),(line2[2],line2[3]))
                
                if inter and line not in usedLines and line2 not in usedLines:
                    
                    intersectPoint = line_intersection(((line[0],line[1]),(width,line[1])),((line2[0],line2[1]),(line2[2],line2[3])))
                    intersectLineDistance = intersectPoint[0] - line[0]
                    
                    if intersectLineDistance > minDistance and intersectLineDistance < maxDistance: 
                        
                        usedLines.append(line)
                        usedLines.append(line2)
                        nodes.append((line[0] + int(intersectLineDistance / 2), line[1], True))
            else: 
                inter = intersect((line[0],line[1]),(line[0],height),(line2[0],line2[1]),(line2[2],line2[3]))
                
                if inter and line not in usedLines and line2 not in usedLines:

                    intersectPoint = line_intersection(((line[0],line[1]),(line[0],height)),((line2[0],line2[1]),(line2[2],line2[3]))) 
                    intersectLineDistance = intersectPoint[1] - line[1]
                    
                    if intersectLineDistance > minDistance and intersectLineDistance < maxDistance: 
                        
                        usedLines.append(line)
                        usedLines.append(line2)
                        nodes.append((line[0], line[1] + int(intersectLineDistance / 2), False))
    return nodes

def removeLoneyPixelNodes(nodes, image): 
    i = 0
    while i < len(nodes) - 1: 
        currentPixel = image[nodes[i][0], nodes[i][1]]
        upPixel = image[nodes[i][0], nodes[i + 1][1]]
        upRightPixel = image[nodes[i + 1][0], nodes[i + 1][1]]
        upLeftPixel = image[nodes[i - 1][0], nodes[i + 1][1]]
        leftPixel = image[nodes[i - 1][0], nodes[i][1]]
        rightPixel = image[nodes[i + 1][0], nodes[i][1]]
        downPixel = image[nodes[i][0], nodes[i - 1][1]]
        downLeftPixel = image[nodes[i - 1][0], nodes[i - 1][1]]
        downRightPixel = image[nodes[i + 1][0], nodes[i - 1][1]]
        
        if currentPixel != upRightPixel and currentPixel != upLeftPixel and currentPixel != leftPixel and currentPixel != rightPixel and currentPixel != downPixel and currentPixel != downLeftPixel and currentPixel != downRightPixel:
            del nodes[i]
        else: 
            i+= 1 

    return nodes

def calculateDistanceBetweenTwoPoints(p1, p2): 
    return ((((p2[0] - p1[0] )**2) + ((p2[1]-p1[1])**2) )**0.5)

def createRoads(nodes, width): 
    forward = []
    left = [] 
    right = []

    for node in nodes: 
        if node[2]: 
            forward.append(node)
        else: 
            if node[0] >= width: 
                right.append(node) 
            else: 
                left.append(node)
    
    forward.sort(key=lambda tup: tup[1])
    left.sort(key=lambda tup: tup[0],reverse=True)
    right.sort(key=lambda tup: tup[0])
    
    lastDistanceLeft = 100000000000
    closestNodeLeft = None

    lastDistanceRight = 100000000000
    closestNodeRight = None

    for node in forward:
        
        dist1 = calculateDistanceBetweenTwoPoints((left[0], left[1]),(node[0],node[1]))
        dist2 = calculateDistanceBetweenTwoPoints((right[0],right[1]),(node[0],node[1]))

        if dist1 < lastDistanceLeft and node[1] < left[0][1]: 
            lastDistanceLeft = dist1
            closestNodeLeft = node
        
        if dist2 < lastDistanceRighti and node[1] < right[0][1]:
            lastDistanceRight = dist2
            closestNodeRight = node
        
        return {"forward":forward, "left": left, "right":right,"intersections":{"left":closestNodeLeft, "right":closestNodeRight}}

def addRoadsOnImage(image, roads): 

    color = (random.randrange(0,255), random.randrange(0,255), random.randrange(0,255))
    for i in range(1, roads["forward"]):
        
        currentPoint = (roads["forward"][i][0], roads["forward"][i][1])
        previousPoint = (roads["forward"][i - 1][0], roads["forward"][i - 1][1])
        cv.line(image,currentPoint, previousPoint,color, 2)
    
    return image

def addNodesOnImage(image, nodes, color):
    if nodes is not None: 
        for node in nodes: 
            if node is None: 
                continue
            image = cv.circle(image,(int(node[0]),int(node[1])),5,(0,255,0),-1)
    image = cv.putText(image,"Nodes: "+str(len(nodes)),(10,20),cv.FONT_HERSHEY_COMPLEX,1,(57,255,20),1,cv.LINE_AA) 
    return image

def addHoughLinesOnImage(image, lines, color):

    if len(lines) == 0:  
        return image

    image = cv.cvtColor(image, cv.COLOR_GRAY2BGR) 
    for line in lines:
        cv.line(image, (line[0],line[1]), (line[2],line[3]), color, config.load()["houghlinesRedLinePixels"])
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
        #binary = removeLoneyPixels(binary) # Removing every lonely pixel, either black or white. 
        canny = convertImageToCanny(binary)
        hough = calculateHoughImage(canny)
        processed = addHoughLinesOnImage(canny, hough, (0,0,255))
       
        #Calculating and adding nodes
        width, height = camera.resolution
        nodes = calculateNodes(hough,15, 250, width, height) 
        #nodes = removeNodesOnWhitePixels(nodes, binary)
        nodes = removeLoneyPixelNodes(nodes, binary)
        roads = createRoads(nodes,width)
        processed = addNodesOnImage(processed,nodes,(0,255,0))
        processed = addRoadsOnImage(processed, roads)
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
