from flask import Flask, render_template, request
from flask_sock import Sock # type: ignore
import threading, multiprocessing, queue
import serialWorker
import time
from feed import Feed
import json
from pudb import set_trace # type: ignore

THREAD_SLEEP_TIME = 0.01

app = Flask(__name__)
webSocket = Sock(app)
inputQueue = queue.Queue(100) #maximum number of items int the queue
outputQueue = queue.Queue(100)
messagingQueue = queue.Queue(100)

# Flask routes____________________________________________________
@app.route('/')
def index(): 
    return render_template('index.html', devices=Feed.description())

# https://blog.miguelgrinberg.com/post/add-a-websocket-route-to-your-flask-2-x-application
@webSocket.route('/sock')
def incomingSocketMessage(sock):
    while True:
#       receive user intent if any
        data: str = sock.receive()
        commands: Optional[list[tuple[int,int]]] 
#       check if this is can be turned into commands
        commands = Feed.commandsFrom(data)
        if not commands is None:
            inputQueue.put(commands)
          
        sock.send(json.dumps(Feed.description()))
#         todo: remove this!
        sock.send(Feed.tree())


#       check for messages to display
        try:
            message = messagingQueue.get(block=False)
            if not message is None:
                sock.send(json.dumps(message))
        except queue.Empty:
            pass

@app.route('/hierarchy', methods=['GET'])
def hierarchy():
    return Feed.tree()
#     return render_template('hierarchy.html', tree=Feed.tree())

@app.route('/hierarchy', methods=['POST'])
def deviceControl():
    commands = Feed.commandsFrom(request.data.decode())
    if not commands is None:
            inputQueue.put(commands)
    return Feed.tree()

@app.route('/setup', methods=['GET'])
def setup():
    return json.dumps(Feed.description())
#     return render_template('setup.html', devices=Feed.description())


# @app.route('/setup', methods=['POST'])
# def deviceActions():
#     try:
#         deviceTitle = request.form['newDeviceTitle']
#         Feed.addDevice(deviceTitle)
#     except KeyError:
#         pass
#     try:
#         deviceToDelete = request.form['deviceToDelete']
#         print(f"server: about to delete {deviceToDelete}")
#         Feed.removeDevice(deviceToDelete)
#     except KeyError:
#         pass
#     try:
#         deviceToMoveChannel = request.form['deviceToMoveChannel']
#         print(f"Moving device {deviceToMoveChannel}")
#         Feed.updateChannel(deviceToMoveChannel, )
#     except KeyError:
#         pass
#     return json.dumps(Feed.description())
# #     return render_template('setup.html', devices=Feed.description())
@app.route('/setup', methods=['POST'])
def deviceActions():
    command = Feed.commandsFrom(request.data.decode())
    return json.dumps(Feed.description())


# queues to serial____and vice versa______________________________
def queueToSerial(inputQueue, serialConnection, stopEvent):
    while not stopEvent.is_set():
#         while True:
        if not inputQueue.empty():
            commands = inputQueue.get()
            print(f"commandToSerial: {commands}")
            if not serialConnection == None and not commands == None:
                serialWorker.write(commands, serialConnection)            
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
    
        

def serialCommsThread(conn, messagingQueue, stopEvent):
    while not stopEvent.is_set():
        messagingQueue.put(f"isConnected,{serialWorker.isConnected()}")
        time.sleep(2)
    conn.close()
    print("comms thread: stopped serial Connection.")
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
    serialThread = threading.Thread(target=serialCommsThread, args=(serialConn, messagingQueue, stopEvent), daemon=True)

    try:
        # go!
        p1.start()
        p2.start()
#         p3.start()
        serialThread.start()
        app.run(debug=True, port=80, host='0.0.0.0')
    except:
        stopEvent.set()
        print("stopping...")
        
    stopEvent.set()
    serialConn.close()
    
    print("finished")
