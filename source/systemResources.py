import psutil
import time
import os
import threading
import MotionControl as motion

thread = None

threadRunning = False

network = {
    "upload":0,
    "download":0
}

def getMemoryUsage():
    return psutil.virtual_memory().percent

def getCpuUsage(): 
    return psutil.cpu_percent()

def getTemperature():
    return psutil.sensors_temperatures()["cpu-thermal"][0].current

def getNetworkUsage(): 
    return network

def getBatteryUsage():
    maxBatteryV = 12.6
    minBatteryV = 9
    
    try:
        currentV = motion.getVoltage()
        return str(rount((maxBatteryV - currentV), 2))
    except:
        return "66"

def start():
    global thread, threadRunning
    print("Initializing system resources thread.")
    threadRunning = True
    thread = threading.Thread(target= run)
    thread.start()

def run():
    global network, threadRunning

    while threadRunning: 
        interval = 1
        t0 = time.time()
        upload0 = psutil.net_io_counters().bytes_sent
        download0 = psutil.net_io_counters().bytes_recv
        time.sleep(interval)
        t1 = time.time()
        upload1 = psutil.net_io_counters().bytes_sent
        download1 = psutil.net_io_counters().bytes_recv
        upload = (upload1 - upload0) / (t1 - t0)
        download = (download1 - download0) / (t1 - t0)
        network["upload"] = round(upload/1000000, 3)
        network["download"] = round(download/100000, 3)

def stop():
    print("Stopping the system resources thread.") 
    global thread, threadRunning
    threadRunning = False
    thread.join()
