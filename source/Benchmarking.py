from datetime import datetime

startTime = None
stopTime = None

def start():
    global startTime
    startTime = datetime.utcnow()
    print("Start time:", startTime.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])

def stop():
    global stopTime
    stopTime = datetime.utcnow()
    print("Stop time:", stopTime.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])

def printExecutionTime():
    print("Execution-time:", (stopTime - startTime))