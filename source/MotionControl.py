from easygopigo3 import EasyGoPiGo3
import config
import threading

defaultSpeed = 0
defaultTurn = 0

speed = 0   # This is the speed of the robot        |Int     | -100 -> 100
rotation = 0    # This is the turning rate of the robot |Float   | -1 -> 1

# Contants for motion control
contant = {
"Max speed": 100,
"Min speed": 0
}

target = None

thread = None
threadRunning = True

robot = EasyGoPiGo3()

# Set
def setTarget(newTarget):
    global target
    target = newTarget
    pass

def setVelocity():
    global speed, rotation, robot, threadRunning
    global defaultSpeed, defaultTurn
    
    while threadRunning:
        try:
            speed = getSpeed()
            rotation = getRotation()
        except:
            print("Did not load speed and turn, stopping for this loop")
            speed = defaultSpeed
            rotation = defaultTurn 
        
        wheelSpeed = [speed - (speed * rotation), speed - (speed * (rotation * -1))] # Calculating the speed values on each wheel. 
        robot.steer(wheelSpeed[0],wheelSpeed[1])


# Get
def getConstantsFromConfig():
    pass

def getVoltage():
    global robot
    return robot.getVoltage()

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
