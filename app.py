from typing import Optional, Any
from flask import Flask, request
import threading, multiprocessing, queue
import serialWorker
import time
from feed import Feed
import json
from pudb import set_trace # type: ignore

THREAD_SLEEP_TIME = 0.01

app = Flask(__name__)
# webSocket = Sock(app)
inputQueue = queue.Queue(100) #maximum number of items int the queue
outputQueue = queue.Queue(100)
# messagingQueue = queue.Queue(100)

# Flask routes____________________________________________________

@app.route('/hierarchy', methods=['GET'])
def hierarchy():
    """
    returns a hierarchical data structure describing the system
    :return: json string
    """
#     todo append useful metadata such as serial conn status here
    return json.dumps(Feed.tree())

@app.route('/hierarchy', methods=['POST'])
def deviceControl():
    """
    Handles POST requests indicating user commands
    returns a hierarchical data structure describing the system
    :return: json string
    """
    commands = Feed.commandsFrom(request.data.decode())
    if not commands is None:
            inputQueue.put(commands)
    return json.dumps(Feed.tree())

@app.route('/setup', methods=['GET'])
def setup():
    """
    returns a list of dicts describing every device
    :return: json string
    """
    return json.dumps(Feed.description())

@app.route('/setup', methods=['POST'])
def deviceActions():
    """
    Handles post requests for the setup page
    returns a list of dicts describing every device
    :return: json string
    """
    command = Feed.commandsFrom(request.data.decode())
    return json.dumps(Feed.description())


# queues to serial____and vice versa______________________________
def queueToSerial(inputQueue, serialConnection, stopEvent):
    """
    Commands added to this queue are sent to the Arduino over the serial connection.
    :param inputQueue: Queue - a multitasking queue
    :param serialConnection: PySerial object - a serial connection object.
    :param stopEvent: a multiprocessing Event - used to tell this process to end.
    """
    while not stopEvent.is_set():
#         while True:
        if not inputQueue.empty():
            commands = inputQueue.get()
            print(f"commandToSerial: {commands}")
            if not serialConnection is None and not commands is None:
                serialWorker.write(commands, serialConnection)            
        time.sleep(THREAD_SLEEP_TIME)
    if serialConnection:
        serialConnection.close()
    print("inputQueue: stopped serial Connection.")
        

def serialToQueue(serialConnection, outputQueue, stopEvent):
#     todo: currently data on the outputQueu is unused.
    """
    This function reads from the serial connection and places the data on a queue.
    This data may represent telemetry or confirm that previous commands have been carried out.
    :param serialConnection: PySerial object - a serial connection object.
    :param outputQueue: Queue - a multitasking queue
    :param stopEvent: a multiprocessing Event - used to tell this process to end.
    """
    while not stopEvent.is_set():
        if not serialConnection is None:
            data = serialWorker.read(serialConnection)
#             print(f"serialToQueue got: {data}")
            outputQueue.put(data)
        time.sleep(THREAD_SLEEP_TIME)
    if serialConnection:
        serialConnection.close()
    print("outputQueue: stopped serial Connection.")
            

def checkHardwareResponses(outputQueue, stopEvent):
    """
    This function reads from the output queue.
    :param outputQueue: Queue - a multitasking queue
    :param stopEvent: a multiprocessing Event - used to tell this process to end.
    """
    while not stopEvent.is_set():
        accumulator: list[str] = []
        if not outputQueue.empty():
#             set_trace() #breakpoint
            accumulator.append(outputQueue.get().decode())
        recievedData: str = ''.join(accumulator)
        repeatedCommands: Optional[str] = Feed.commandsFromSerial(recievedData)
        #     todo: currently data on the outputQueue is unused.
        time.sleep(THREAD_SLEEP_TIME)

# todo: a keep alive thread.

# def serialCommsThread(conn, messagingQueue, stopEvent):
#     while not stopEvent.is_set():
#         messagingQueue.put(f"isConnected,{serialWorker.isConnected()}")
#         time.sleep(2)
#     conn.close()
#     print("comms thread: stopped serial Connection.")
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
    # thread for reading from input queue and writing to serial
    p1 = threading.Thread(target=queueToSerial, args=(inputQueue, serialConn, stopEvent), daemon=True)
    # tread for reading serial and sending to output queue
    p2 = threading.Thread(target=serialToQueue, args=(serialConn, outputQueue, stopEvent), daemon=True)
    # thread for printing Arduino output
    p3 = threading.Thread(target=checkHardwareResponses, args=(outputQueue, stopEvent), daemon=True)
#     thread for monitoring the serial connection
#     serialThread = threading.Thread(target=serialCommsThread, args=(serialConn, messagingQueue, stopEvent), daemon=True)

    try:
        # go!
        p1.start()
        p2.start()
        p3.start()
#         serialThread.start()
        app.run(debug=True, port=80, host='0.0.0.0')
    except:
        stopEvent.set()
        print("stopping...")
        
    stopEvent.set()
    
    if serialConn:
        serialConn.close()
    
    print("finished")
    
    
