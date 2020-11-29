import threading
import ImageProcessing as ip
import UserInterface as ui
import systemResources as sr
import MotionControl as mc
import time
import config

print("Starting I/O module")

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
    while True:
        #ip.updateCameraValues()
        ui.setOriginalImage(ip.getOriginalImage())
        ui.setGrayImage(ip.getGreyImage())
        ui.setBinaryImage(ip.getBinaryImage())
        ui.setProcessedImage(ip.getProcessedImage())
except KeyboardInterrupt:
    print("Starting shutdown.")
    ip.stop()
    ui.stop()
    sr.stop()
    mc.stop()
    print("Shutdown complete.")
