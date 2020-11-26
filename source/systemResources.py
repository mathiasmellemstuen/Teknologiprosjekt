import psutil
import time
import os
import threading

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

def startSystemResourcesThread():
    print("Initializing system resources thread.")
    thread = threading.Thread(target= run)
    thread.start()

def run():
    global network

    while True: 
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
        network["download"] = round(download/1000000, 3)