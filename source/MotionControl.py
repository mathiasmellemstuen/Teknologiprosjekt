from easygopigo3 import EasyGoPiGo3
import config

defaltSpeed = 0
defaultTurn = 0

speed = 10   # This is the speed of the robot       |Int     | -100 -> 100
turn = 0    # This is the turning rate of the robo |Float   | -1 -> 1

robot = EasyGoPiGo3()

def getSpeed():
    return config.load()["speed"]

def getAngle():
    return config.load()["rotation"]

def setVelosity():
    global speed, turn, robot
    
    try:
        speed = 10# getSpeed()
        turn = 0# getTurn()
    except:
        print("Did not load speed and turn, stopping for this loop")
        speed = defaultSpeed
        turn = defaultTurn 

    turn = [speed * turn, speed * (turn * -1)]

    print(turn)

    robot.steer(0, 0)

while True:
    setVelosity()
