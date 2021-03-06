import threading
import ImageProcessing as ip
import UserInterface as ui
import systemResources as sr
import MotionControl as mc
import time
import config
import subprocess

print("Starting I/O module")
subprocess.call(["wall", "Robot staring"])

running = True
config.load() 
time.sleep(1)
print("Done: Loading config file:") 

#Starting threads
print("Starting all threads")
ip.start()
ui.start()
sr.start()
mc.start()

time.sleep(2) # Waiting for the initialization of the modules above. 
print("All modules initialized. Started successfully")
try:
    while running:
        ui.setOriginalImage(ip.getOriginalImage())
        ui.setGrayImage(ip.getGreyImage())
        ui.setBinaryImage(ip.getBinaryImage())
        ui.setProcessedImage(ip.getProcessedImage())
        mc.setNodes(ip.getRoads())
except KeyboardInterrupt:
    print("Starting shutdown.")
    running = False
    ip.stop()
    ui.stop()
    sr.stop()
    mc.stop()
    print("Shutdown complete.")
    subprocess.call(["wall", "Robot shutdown"])
    exit()
