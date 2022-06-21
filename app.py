from flask import Flask, render_template, request
from flask_sock import Sock
import threading, multiprocessing, queue
import serialWorker
import time
from feed import Feed
import json
from pudb import set_trace

THREAD_SLEEP_TIME = 0.01

app = Flask(__name__)
webSocket = Sock(app)
# inputQueue = multiprocessing.Queue(100) #maximum number of items int the queue
# outputQueue = multiprocessing.Queue(100)
inputQueue = queue.Queue(100) #maximum number of items int the queue
outputQueue = queue.Queue(100)

# Flask routes____________________________________________________
@app.route('/')
def index(): 
    return render_template('index.html', devices=Feed.description())

# https://blog.miguelgrinberg.com/post/add-a-websocket-route-to-your-flask-2-x-application
@webSocket.route('/sock')
def incomingSocketMessage(sock):
    while True:
        data = sock.receive()
        print(f"route collected some data: {data}, type: {type(data)}")
#         check if this is allowed
        command = Feed.commandFrom(data)
        if not command == None:
#             set_trace() #breakpoint
            inputQueue.put(command)
        sock.send(json.dumps(Feed.description()))

@app.route('/setup', methods=['GET'])
def setup():  #Flask view function
    return render_template('setup.html', devices=Feed.description())


# queues to serial____and vice versa______________________________

def queueToSerial(inputQueue, serialConnection, stopEvent):
    while not stopEvent.is_set():
        while True:
            if not inputQueue.empty():
                command = inputQueue.get()
                print(f"commandToSerial: {command}")
                if not serialConnection == None and not command == None:
                    serialWorker.write(serialConnection, command)            
            time.sleep(THREAD_SLEEP_TIME)
    serialConnection.close()
    print("inputQueue: stopped serial Connection.")
        

def serialToQueue(serialConnection, outputQueue, stopEvent):
    while not stopEvent.is_set():
        if serialConnection != None:
            data = serialWorker.read(serialConnection)
#             print(f"serialToQueue got: {data}")
            outputQueue.put(data)
        time.sleep(THREAD_SLEEP_TIME)
    serialConnection.close()
    print("outputQueue: stopped serial Connection.")
            
def checkHardwareResponses(queue, stopEvent):
    while not stopEvent.is_set():
        accumulator = []
        if not queue.empty():
#             set_trace() #breakpoint
            accumulator.append(queue.get())
        repeatedCommands = Feed.commandsFromSerial(accumulator)
        if repeatedCommands != None:
            for command in repeatedCommands:
                print(f"repeatedCommand: {command}")
#       Feed.updateDB(repeatedCommands)                
        time.sleep(THREAD_SLEEP_TIME)
# -----------------------------------------------------------------



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
    p1 = threading.Thread(target=queueToSerial, args=(inputQueue, serialConn, stopEvent), daemon=True)
    # tread for reading serial and sending to socket
    p2 = threading.Thread(target=serialToQueue, args=(serialConn, outputQueue, stopEvent), daemon=True)
    # thread for printing Arduino output
#     p3 = threading.Thread(target=checkHardwareResponses, args=(outputQueue, stopEvent), daemon=True)


    try:
        # go!
        p1.start()
        p2.start()
#         p3.start()
        app.run(debug=True, port=80, host='0.0.0.0')
    except:
        stopEvent.set()
        print("stopping...")
        
    stopEvent.set()
    serialConn.close()
    
    print("finished")
