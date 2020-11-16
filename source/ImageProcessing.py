from io import BytesIO
from time import sleep
from picamera import PiCamera
from datetime import datetime
#warmup = 2 # In seconds
#print("Staring image processing module.")

#stream = BytesIO() 
#camera = PiCamera() 
#camera.start_preview()

#print("Camera warmup: starting")
#sleep(warmup)
#print("Camera warmup: finished")

#camera.capture(stream, 'jpeg')


camera = PiCamera()
camera.resolution = (1024, 768)
camera.start_preview()

sleep(2)

print("TIME BEFORE:", datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])
camera.capture("/var/www/control-panel/capture.jpg")
print("TIME AFTER:", datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])