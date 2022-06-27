from typing import Optional, Any

import serial # type: ignore
import time

MEGA        = {"device" : "/dev/cu.usbmodem141401", "baud" : 250000, "timeout" : 1}
NANO        = {"device" : "/dev/cu.usbserial-14120", "baud" : 250000, "timeout" : 1}
TERMINAL    = {"device" : "/dev/ttys005", "baud" : 9600, "timeout" : 1}

modem = MEGA

startSym = "-"
endSym = "^"

def getSerialConnection():
    conn = serial.Serial(modem["device"], modem["baud"], timeout=modem["timeout"])
    time.sleep(3)
#     conn.write('\r'.encode())
#     conn.reset_input_buffer()
#     conn.reset_output_buffer()
    conn.write(startSym.encode()) #put Arduino into ready state
    return conn
       
def write(commands: list[int], conn) -> None:
    for command in commands:
        commandBytes: bytes = startSym.encode('ascii') + bytes(command) + endSym.encode('ascii')
        numberOfBytesSent: int = conn.write(commandBytes)
#     print(f"serialWorker sent {numberOfBytesSent} bytes: {commandBytes}")
    
def read(conn) -> bytes:
    data = conn.read_until(expected='\r\n')
    # if len(data) != 0:
#         print(f"serialWorker read {len(data)}: {data}")
    return data
    
def status(conn) -> dict[str, Any]:
    status = {"modem" : conn.name, "rate" : conn.baudrate, "isConnected" : conn.is_open,
            "port": conn.port, "timeout" : conn.timeout}
    return status