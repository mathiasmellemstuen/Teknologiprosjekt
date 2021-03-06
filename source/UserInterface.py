from flask import Flask, jsonify, request, Response, render_template
import threading
import config
import systemResources as sysres
import logging
import Benchmarking as b
import time

app = Flask(__name__, static_url_path="", static_folder="static")

#Changing logging level to error.
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

originalImage = None
grayImage = None
binaryImage = None
processedImage = None

thread = None
threadRunning = True

@app.route('/')
def root():
    return app.send_static_file('index.html')

@app.route('/api', methods=['GET'])
def hello_world():
    return jsonify(text)

@app.route('/api', methods=['POST'])
def post():
    newText = request.get_json(force=True)
    text.append(newText)

    return jsonify(text)

# System resources ------- 
@app.route("/api/resources", methods=["GET"])
def resourcesGet(): 
    data = {
        "cpu": sysres.getCpuUsage(),
        "ram": sysres.getMemoryUsage(),
        "temp": sysres.getTemperature(),
        "net": sysres.getNetworkUsage(),
        "battery": sysres.getBatteryUsage()
    }
    return jsonify(data)

# Config -------
@app.route('/api/config', methods=['GET'])
def configGet():
    return jsonify(config.load())

@app.route('/api/config', methods=['POST'])
def configPost():
    newConfig = request.get_json(force=True)
    config.save(newConfig)
    return jsonify(config.load())


# Camera Streaming -------
## Original Image -------
def genOriginalImage():
    global originalImage, threadRunning

    while threadRunning:
        #get camera frame
        yield b'--frame\r\nContent-Type: image/jpeg\r\n\r\n'
        yield originalImage
        yield b'\r\n\r\n'

@app.route('/api/video/original')
def videoFeed():
    return Response(genOriginalImage(), mimetype = "multipart/x-mixed-replace; boundary=frame")

def setOriginalImage(image): 
    global originalImage
    originalImage = image

## Gray image -------
def genGrayImage():
    global grayImage, threadRunning

    while threadRunning:
        #get camera frame
        yield b'--frame\r\nContent-Type: image/jpeg\r\n\r\n'
        yield grayImage
        yield b'\r\n\r\n'

@app.route('/api/video/gray')
def videoGray():
    return Response(genGrayImage(), mimetype = "multipart/x-mixed-replace; boundary=frame")

def setGrayImage(image):
    global grayImage
    grayImage = image

## Binary image -------
def genBinaryImage():
    global binaryImage, threadRunning

    while threadRunning:
        #get camera frame
        yield b'--frame\r\nContent-Type: image/jpeg\r\n\r\n'
        yield binaryImage
        yield b'\r\n\r\n'

@app.route('/api/video/binary')
def videoBinary():
    return Response(genBinaryImage(), mimetype = "multipart/x-mixed-replace; boundary=frame")

def setBinaryImage(image):
    global binaryImage
    binaryImage = image

## Processed image -------
def genProcessedImage():
    global processedImage, threadRunning

    while threadRunning:  
        yield b'--frame\r\nContent-Type: image/jpeg\r\n\r\n'
        yield processedImage
        yield b'\r\n\r\n'

@app.route('/api/video/processed')
def videoProcessed():
    return Response(genProcessedImage(), mimetype = "multipart/x-mixed-replace; boundary=frame")

def setProcessedImage(image):
    global processedImage
    processedImage = image

def run(): 
    app.run(host='0.0.0.0', debug = False, port=80)

def start():
    global thread, threadRunning 
    print("Initializing user interface thread.")
    threadRunning = True
    thread = threading.Thread(target= run) 
    thread.setDaemon(True)
    thread.start()
    
def stop():
    global thread, threadRunning 
    print("Stopping user interface thread.")
    threadRunning = False
    #request.environ.get("werkzeug.server.shutdown")
    #thread.join()
