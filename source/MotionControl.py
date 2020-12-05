from easygopigo3 import EasyGoPiGo3
import config
import threading
import math
import numpy as np

defaultSpeed = 0
defaultTurn = 0

speed = 0       # This is the speed of the robot        |Int     | -100 -> 100
rotation = 0    # This is the turning rate of the robot |Float   | -1 -> 1

# Contants for motion control
constants = {
    "maxSpeed": 100,
    "minSpeed": 0,
    "distanceToSlowdown": 10,
    "errorMarginNodeInside": 5,
    "errorMarginNodeCleaning": 5,

    "minClosestNodeIgnore": 5,

    "cammeraWidth": 500,    # Get form imageProsessing
    "cammeraHeight": 500    # Get form imageProsessing
}

nodes = None
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

#   Noes from ImageProsessing
#       Representing all of the nodes on the road
#
#   [
#   (x, y),     # This is the middle point the "road"
#   ]



thread = None
threadRunning = True

robot = EasyGoPiGo3()

# calculations
def calcAngle(nextNode):
    theta = math.atan(nextNode[1] / nextNode[0])

    return math.sin(theta)

def calcSpeed(nextNode):
    global constants

    speed = int(constants["maxSpeed"])
    minSpeed = int(constants["minSpeed"])
    distanceToSlowdown = int(constants["distanceToSlowdown"])

    length = math.sqrt(math.pow(nextNode[0], 2), math.pow(nextNode[1], 2))

    if length > distanceToSlowdown:
        speed = int(constants["maxSpeed"])
    elif length < distanceToSlowdown:
        distLeft = distanceToSlowdown - length
        speed = speed / distLeft

    speed = speed if speed <= minSpeed else minSpeed
    return speed

# Set 
def setNodes(newNodes):
    global nodes
    nodes = newNodes

def setSpeed():
    global target, constants
    speed = constants["maxSpeed"]
    node = getNode()


    


    


def setVelocity():  # Needs a rework (or the functions it is using)
    global speed, rotation, robot, threadRunning
    global defaultSpeed, defaultTurn
    global target, constants
    
    while threadRunning:
        try:    # if there is some error setting the speed, then just stop the robot.
            speed = getSpeed()
            rotation = getRotation()
        except:
            speed = defaultSpeed
            rotation = defaultTurn 
        
        wheelSpeed = [speed - (speed * rotation), speed - (speed * (rotation * -1))] # Calculating the speed values on each wheel. 
        robot.steer(wheelSpeed[0],wheelSpeed[1])


# Get 
def getNextNode():  # Might replace getNode(), depending on what featsured is needed
    global nodes, constants

    nextNode = nodes[0]

    for node in nodes:
        if node[0] == nextNode[0] and node[1] == nextNode[1]:
            continue
        else:   # see if the node is closer then nextNode
            if abs(node[1] - int(constants["cammeraWidth"])) > abs(nextNode[1] - int(constants["cammeraWidth"])) and int(constants["minClosesNodeIgnore"]) < nextNode[0] < node[0]:
                nextNode = node

    return nextNode

def getDistanceToNextNode(nextNode):
    
    Ax = nextNode[0] - int(constants["cammeraWidth"])
    Ay = nextNode[1]

    return abs(math.sqrt(Ax**2 + Ay**2))

def getAngleToNextNode():
    # Here i can add some sin, cos, tan magic to calculate the real distanse, or I can be lazy and just base it of some distance, all depending on time.
    global constants

    Ax = nextNode[0] - int(constants["cammeraWidth"])
    Ay = nextNode[1]

    theta = math.atan2(Ay,Ax)
    theta = np.atan2(Ay, Ax)

    return theta    # Deg

def degToPrecent(deg):
    totalTurnDeg = 180 # Deg, can change to whant ever is smartest

    return deg/totalTurnDeg * 100


def getNode():
    global target, constants

    nextNode = [int(target["nodes"][i]["x"]), int(target["nodes"][i]["y"])]
    
    i = 0
    while nextNode[i] and nextNode[i] >= int(constants["errorMargin"]): # ?
        i += 1
        nextNode = [int(target["nodes"][i]["x"]), int(target["nodes"][i]["y"])]

    return nextNode

def cleanNodes(nodes):  # This probaly needs a rework...
    global constants

    currentNode = {}

    i = 0
    while i < len(nodes):
        currentNode = nodes[i]

        index = 0
        while index < len(nodes):
            if index <= i or index == len(nodes):
                continue
                index += 1
            else:
                a1 = (int(nodes[index]["y"]) - int(currentNode["y"])) / (int(nodes[index]["x"]) - int(currentNode["x"]))
                a2 = (int(nodes[index + 1]["y"]) - int(nodes[index]["y"])) / (int(nodes[index + 1]["x"]) - int(nodes[index]["x"]))

                if a1 - a2 < int(constants["errorMarginNodeCleaning"]):
                    del nodes[index]

            index += 1
        i += 1
    return nodes
        




def getConstantsFromConfig():
    pass

def getVoltage():
    global robot
    return robot.volt()

def getSpeed():     # Old, can probaly remove
    global speed
    speed = config.load()["speed"]
    return speed

def getRotation():  # Old, can probaly remove
    global rotation 
    rotation = config.load()["rotation"]
    return rotation

def start():    # Function to start the robot
    global thread, threadRunning
    threadRunning = True
    thread = threading.Thread(target = setVelocity)
    thread.start()

def stop():   # Function that is called when the script ends
    global speed, rotation, thread, threadRunning

    speed = 0
    rotation = 0
    threadRunning = False
    robot.stop()
    thread.join()
