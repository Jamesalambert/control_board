from flask import Flask, render_template
from flask_sock import Sock
import threading, multiprocessing
import serialWorker
import time
from feed import Feed
import json

app = Flask(__name__)
webSocket = Sock(app)
inputQueue = multiprocessing.Queue()
outputQueue = multiprocessing.Queue()

@app.route('/')
def index():  #Flask view function
    return render_template('index.html', devices=Feed.description())
    
@app.route('/setup')
def setup():  #Flask view function
    return render_template('setup.html', devices=Feed.description())

# https://blog.miguelgrinberg.com/post/add-a-websocket-route-to-your-flask-2-x-application
@webSocket.route('/sock')
def addToQueue(sock):
    while True:
        data = sock.receive()
        print(f"route collected some data: {data}, type: {type(data)}")
#         check if this is allowed
        command = Feed.commandFrom(data)
        inputQueue.put(command)
        
        sock.send(json.dumps(Feed.description()))


def queueToSerial(inputQueue, serialConnection):
    while True:
        if inputQueue.empty() == False:
            command = inputQueue.get()
            print(f"commandToSerial: {command}")
            if not serialConnection == None and not command == None:
                serialWorker.write(serialConnection, command)            
        time.sleep(0.1)

def serialToQueue(serialConnection, outputQueue, stopEvent):
    while not stopEvent.is_set():
        if not serialConnection == None:
            data = serialWorker.read(serialConnection).strip()
            print(f"serialToQueue got: {data}")
            outputQueue.put(data)
        time.sleep(0.1)
    serialConnection.stop()
    print("stopped serial Connection.")
            
def checkHardwareResponses(queue):
    while True:
        if queue.empty() == False:
            repeatedCommand = queue.get().decode()
            repeatedCommand = [int(c) for c in repeatedCommand]
            if len(repeatedCommand) == 2:
                print(f"repeatedCommand: {repeatedCommand}")
                Feed.updateDB(repeatedCommand[0], repeatedCommand[1])
#             push changes via websocket
                
        time.sleep(0.1)


if __name__ == '__main__':
    # get serial port
    try:
        serialConn = serialWorker.getSerialConnection()
    except:
        serialConn = None
        print("Couldn't get serial connection, running server anyway...")
    
    
    # event object to close serial port
    stopEvent = threading.Event()
    # thread for reading from socket and writing to serial
    p1 = threading.Thread(target=queueToSerial, args=(inputQueue, serialConn), daemon=True)
    # tread for reading serial and sending to socket
    p2 = threading.Thread(target=serialToQueue, args=(serialConn, outputQueue, stopEvent), daemon=True)
    # thread for printing Arduino output
    p3 = threading.Thread(target=checkHardwareResponses, args=(outputQueue,), daemon=True)

    # go!
    p1.start()
    p2.start()
    p3.start()
    
    try:
        app.run(debug=True, port=80, host='0.0.0.0')
    except KeyboardInterrupt:
        try:
            stopEvent.set()
        except NameError:
            print("didn't close Serial connection because it didn't exist.")

        
#     serialConn.close()