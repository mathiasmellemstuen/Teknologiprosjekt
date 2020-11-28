from easygopigo3 import EasyGoPiGo3
import config

defaltSpeed = 0
defaultTurn = 0

speed = 0   # This is the speed of the robot       |Int     | -100 -> 100
turn = 0    # This is the turning rate of the robo |Float   | -1 -> 1

robot = EasyGoPiGo3()

def getSpeed():
    return config.load()["speed"]

def getAngle():
    return config.load()["rotation"]

def setVelosity():
    global speed, turn, robot
    
    try:
        speed = getSpeed()
        turn = getTurn()
    except:
        print("Did not load speed and turn, stopping for this loop")
        speed = defaultSpeed
        turn = defaultTurn 

    turn = [speed * turn, speed * (turn * -1)]

    robot.steer(turn[0], turn[1])
