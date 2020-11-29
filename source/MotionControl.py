from easygopigo3 import EasyGoPiGo3
import config
import threading

defaultSpeed = 0
defaultTurn = 0

speed = 0   # This is the speed of the robot        |Int     | -100 -> 100
turn = 0    # This is the turning rate of the robot |Float   | -1 -> 1

thread = None

robot = EasyGoPiGo3()

def getSpeed():
    speed = config.load()["speed"]
    return speed

def getAngle():
    rotation = config.load()["rotation"]
    return rotation

def setVelosity():
    global speed, turn, robot
    global defaultSpeed, defaultTurn

    try:
        speed = getSpeed()
        turn = getTurn()
    except:
        print("Did not load speed and turn, stopping for this loop")
        speed = defaultSpeed
        turn = defaultTurn 

    turn = [speed * turn, speed * (turn * -1)]

def start():    # Function to start the robot
    global thread

    thread = threading.Thread(target = setVelosity)

def stop():   # Function that is called when the script ends
    global speed, turn, thread

    speed = 0
    turn = 0

    robot.stop()
    thread.join()
