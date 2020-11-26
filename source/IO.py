import threading
import ImageProcessing as ip
import UserInterface as ui
import systemResources as sr
import time
import config

print("Starting I/O module")

config.load() 
time.sleep(1)
print("Done: Loading config file:") 

ip.startImageProcessingThread()
ui.startUserInterfaceThread()
sr.startSystemResourcesThread()

time.sleep(2) # Waiting for the initialization of the modules above. 
print("All modules initialized. Started successfully") 

while True:
    ui.setOriginalImage(ip.getOriginalImage())
    ui.setGrayImage(ip.getGreyImage())
    ui.setBinaryImage(ip.getBinaryImage())
    ui.setCannyImage(ip.getCannyImage())