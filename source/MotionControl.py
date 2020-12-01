from easygopigo3 import EasyGoPiGo3
import config
import threading
import math

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
    "errorMarginNodeCleaning": 5
}

target = None
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
def setTarget(newTarget):
    global target
    target = newTarget

def setSpeed():
    global target, constants
    speed = constants["maxSpeed"]
    node = getNode(target)


    


    


def setVelocity():
    global speed, rotation, robot, threadRunning
    global defaultSpeed, defaultTurn
    global target, constants
    
    while threadRunning:
        try:
            speed = getSpeed()
            rotation = getRotation()
        except:
            #print("Did not load speed and turn, stopping for this loop")
            speed = defaultSpeed
            rotation = defaultTurn 
        
        wheelSpeed = [speed - (speed * rotation), speed - (speed * (rotation * -1))] # Calculating the speed values on each wheel. 
        robot.steer(wheelSpeed[0],wheelSpeed[1])


# Get 
def getNode():
    global target, constants

    nextNode = [int(target["nodes"][i]["x"]), int(target["nodes"][i]["y"])]

    i = 0
    while nextNode[i] and nextNode[i] >= int(constants["errorMargin"]):
        i += 1
        nextNode = [int(target["nodes"][i]["x"]), int(target["nodes"][i]["y"])]

    return nextNode

def cleanNodes(nodes):
    global constants

    currentNode = {}

    i = 0
    while i < len(nodes):
        currentNode = nodes[i]
        
        while index < len(nodes):
            if index <= i:
                continue
            elif index = range(len(nodes)):
                continue
            elif:
                a1 = (int(nodes[index]["y"]) - int(currentNode["y"])) / (int(nodes[index]["x"]) - int(currentNode["x"]))
                a2 = (int(nodes[index + 1]["y"]) - int(nodes[index]["y"])) / (int(nodes[index + 1]["x"]) - int(nodes[index]["x"]))

                if a1 - a2 < int(constants["errorMarginNodeCleaning"]):
                    del nodes[index]

    return nodes
        

def getConstantsFromConfig():
    pass

def getVoltage():
    global robot
    return robot.volt()

def getSpeed():
    global speed
    speed = config.load()["speed"]
    return speed

def getRotation():
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
