import serial
import time

modem = "/dev/cu.usbmodem141401"
baud_rate = 9600
timeout = 1 #seconds

def getSerialConnection():
    conn = serial.Serial(modem, baud_rate, timeout=timeout)
    return conn
       
def write(conn, command):
    commandBytes = bytes(command)
    numberOfBytesSent = conn.write(commandBytes)
    print(f"serialWorker sent {numberOfBytesSent} bytes: {commandBytes}")
    
def read(conn):
    data = conn.readline()
    print(f"serialWorker read {len(data)}: {data}")
    return data    