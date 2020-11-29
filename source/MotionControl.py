from easygopigo3 import EasyGoPiGo3
import config
import threading

defaultSpeed = 0
defaultTurn = 0

speed = 0   # This is the speed of the robot        |Int     | -100 -> 100
rotation = 0    # This is the turning rate of the robot |Float   | -1 -> 1

thread = None

robot = EasyGoPiGo3()

def getSpeed():
    global speed
    speed = config.load()["speed"]
    return speed

def getRotation():
    global rotation 
    rotation = config.load()["rotation"]
    return rotation

def setVelosity():
    global speed, rotation, robot
    global defaultSpeed, defaultTurn

    try:
        speed = getSpeed()
        rotation = getRotation()
    except:
        print("Did not load speed and turn, stopping for this loop")
        speed = defaultSpeed
        rotation = defaultTurn 

    rotation = [speed * rotation, speed * (rotation * -1)]

def start():    # Function to start the robot
    global thread

    thread = threading.Thread(target = setVelosity)

def stop():   # Function that is called when the script ends
    global speed, rotation, thread

    speed = 0
    rotation = 0

    robot.stop()
    thread.join()
