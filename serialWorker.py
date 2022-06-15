import serial
import time

MEGA = "/dev/cu.usbmodem141401"
NANO = "/dev/cu.usbserial-14120"
modem = MEGA

baud_rate = 9600
timeout = 1 #seconds

startSym = "-"
endSym = "\n"

def getSerialConnection():
    conn = serial.Serial(modem, baud_rate, timeout=timeout)
    return conn
       
def write(conn, command):
    commandBytes = startSym.encode('ascii') + bytes(command) + endSym.encode('ascii')
    numberOfBytesSent = conn.write(commandBytes)
#     print(f"serialWorker sent {numberOfBytesSent} bytes: {commandBytes}")
    
def read(conn):
    data = conn.readline().strip()
#     print(f"serialWorker read {len(data)}: {data}")
    return data    