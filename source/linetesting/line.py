import matplotlib.pyplot as plt
import cv2
import numpy as np
import random as rn
import math

def calculateLineRadians(x1,y1,x2,y2):
    dx = x2 - x1
    dy = y2 - y1
    return math.atan2(dy,dx)

def convertAngle0To2Pi(a):
    return a if a >= 0.0 else 2 * math.pi + a

def calculateRadiansBetweenTwoNodes(p1,p2):
    radians1 = calculateLineRadians(p2[0],p2[1],p1[0],p1[1])
    radians2 = calculateLineRadians(p2[0],p2[1],p1[0],p1[1])
    
    radians1 = convertAngle0To2Pi(radians1)
    radians2 = convertAngle0To2Pi(radians2)
    return abs(radians1-radians2)

def distanceBetweenTwoPoints(p1,p2):
    return ((((p2[0] - p1[0] )**2) + ((p2[1]-p1[1])**2) )**0.5)

def findClosestNode(fromNode): 
    global newLines

    closestNode = (100000,1000000)
    for node in newLines: 
        if fromNode != node: 
            if distanceBetweenTwoPoints((fromNode[2], fromNode[3]), (node[0], node[1])) < distanceBetweenTwoPoints((fromNode[2], fromNode[3]), (closestNode[0], closestNode[1])):
                closestNode = node
    return closestNode

def findLine(currentLines, startingNode, validDistance, validAngle):

    line = []
    line.append(startingNode)
    
    for i in range(0,len(currentLines)):
        currentNode = line[len(line) - 1]
        currentLineAngle = calculateRadiansBetweenTwoNodes((currentNode[0],currentNode[1]), (currentNode[2], currentNode[3]))
        closestNode = findClosestNode(currentNode)
        distanceToClosestNode = distanceBetweenTwoPoints((currentNode[2], currentNode[3]), (closestNode[0], closestNode[1]))
        angleToClosestNode = calculateRadiansBetweenTwoNodes((currentNode[2], currentNode[3]),(closestNode[0],closestNode[1]))
        print("Distance to closest node:", distanceToClosestNode)
        print("Angle to closest node:", angleToClosestNode)
        if distanceToClosestNode > validDistance or angleToClosestNode > validAngle:
            return line

    return line

def randomColor(): 
    return (rn.randrange(0,255),rn.randrange(0,255),rn.randrange(0,255))

def setMiddlePoint(a1, a2, plot):
    # Finde the range of x in array 1
    min_a1_x, max_a1_x = min(a1[:,0]), max(a1[:,0])
    new_a1_x = np.linspace(min_a1_x, max_a1_x, 100)
    a1_coefs = np.polyfit(a1[:,0], a1[:,1], 3)
    new_a1_y = np.polyval(a1_coefs, new_a1_x)

    # Finde the range of x in array 2
    min_a2_x, max_a2_x = min(a2[:,0]), max(a2[:,0])
    new_a2_x = np.linspace(min_a2_x, max_a2_x, 100)
    a2_coefs = np.polyfit(a2[:,0], a2[:,1], 3)
    new_a2_y = np.polyval(a2_coefs, new_a2_x)

    midx = [np.mean([new_a1_x[i], new_a2_x[i]]) for i in range(100)]
    midy = [np.mean([new_a1_y[i], new_a2_y[i]]) for i in range(100)]

    if plot:
        plt.plot(a1[:,0], a1[:,1],c='black')
        plt.plot(a2[:,0], a2[:,1],c='black')
        plt.plot(midx, midy, '--', c='black')
        plt.show()

def setMiddlePoint2(a1, a2, plot):
    min_a1_x, max_a1_x = min(a1[:,0]), max(a1[:,0])
    min_a2_x, max_a2_x = min(a2[:,0]), max(a2[:,0])

    new_a1_x = np.linspace(min_a1_x, max_a1_x, 100)
    new_a2_x = np.linspace(min_a2_x, max_a2_x, 100)

    new_a1_y = np.interp(new_a1_x, a1[:,0], a1[:,1])
    new_a2_y = np.interp(new_a2_x, a2[:,0], a2[:,1])

    midx = [np.mean([new_a1_x[i], new_a2_x[i]]) for i in range(100)]
    midy = [np.mean([new_a1_y[i], new_a2_y[i]]) for i in range(100)]

    if plot:        
        plt.plot(a1[:,0], a1[:,1],c='black')
        plt.plot(a2[:,0], a2[:,1],c='black')
        plt.plot(midx, midy, '--',c='black')
        plt.show()


img = cv2.imread('lane3.png')
gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

kernel_size = 5
blur_gray = cv2.GaussianBlur(gray,(kernel_size, kernel_size),1)

low_threshold = 50
high_threshold = 150
edges = cv2.Canny(blur_gray, low_threshold, high_threshold)

kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
dilate = cv2.dilate(edges, kernel, iterations=1)

cv2.imwrite('blur_gray3.jpg', blur_gray)
cv2.imwrite('edges3.jpg', edges)
cv2.imwrite('dilate3.jpg', dilate)

rho = 1
theta = np.pi / 180
threshold = 20
min_line_length = 10
max_line_gap = 50
line_image = np.copy(img) * 0
lines = cv2.HoughLinesP(edge, rho, theta, threshold, np.array([]),min_line_length, max_line_gap)

newLines = []

for line in lines:
    for x1,y1,x2,y2 in line:
        newLines.append((x1, y1, x2, y1))

newLines.sort(key=lambda tup: tup[0])
errorMargin = 10

foundLines = []

for line in newLines: 
    if line[0] > errorMargin:
        break
    else:
        foundLines.append(findLine(newLines, line,200,0.2))

for line in foundLines: 
    color = randomColor() 
    for points in line:
        cv2.line(line_image,(points[0],points[1]),(points[2],points[3]),color,1)

cv2.imwrite('houghlines3.jpg',line_image)
