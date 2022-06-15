import serial
import time

MEGA = "/dev/cu.usbmodem141401"
NANO = "/dev/cu.usbserial-14120"
modem = MEGA

baud_rate = 250000
timeout = 1 #seconds

startSym = "-"
endSym = "^"

def getSerialConnection():
    conn = serial.Serial(modem, baud_rate, timeout=timeout)
    conn.reset_input_buffer()
    conn.reset_output_buffer()
    return conn
       
def write(conn, command):
    commandBytes = startSym.encode('ascii') + bytes(command) + endSym.encode('ascii')
    numberOfBytesSent = conn.write(commandBytes)
#     print(f"serialWorker sent {numberOfBytesSent} bytes: {commandBytes}")
    
def read(conn):
    data = conn.read_until(expected='\n').decode().strip()
    if len(data) != 0:
        print(f"serialWorker read {len(data)}: {data}")
    return data    