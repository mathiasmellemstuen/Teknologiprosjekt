from easygopigo3 import EasyGoPiGo3
import config
import threading

defaltSpeed = 0
defaultTurn = 0

<<<<<<< HEAD
speed = 0   # This is the speed of the robot       |Int     | -100 -> 100
turn = 0    # This is the turning rate of the robot|Float   | -1 -> 1

thread = None
=======
speed = 10   # This is the speed of the robot       |Int     | -100 -> 100
turn = 0    # This is the turning rate of the robo |Float   | -1 -> 1
>>>>>>> 936234fd86037ea5cb55dd5d2543fed8fa5fd991

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
<<<<<<< HEAD
        speed = getSpeed()
        turn = getAngle()
=======
        speed = 10# getSpeed()
        turn = 0# getTurn()
>>>>>>> 936234fd86037ea5cb55dd5d2543fed8fa5fd991
    except:
        print("Did not load speed and turn, stopping for this loop")
        speed = defaultSpeed
        turn = defaultTurn 

    turn = [speed * turn, speed * (turn * -1)]

    print(turn)

<<<<<<< HEAD
def start():    # Function to start the robot
    global thread

    thread = threading.Thread(target = setVelosity)

def stop():   # Function that is called when the script ends
    global speed, turn, thread

    speed = 0
    turn = 0

    robot.stop()
    thread.join()

while true:
=======
    robot.steer(0, 0)

while True:
>>>>>>> 936234fd86037ea5cb55dd5d2543fed8fa5fd991
    setVelosity()
