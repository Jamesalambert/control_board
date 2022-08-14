from typing import Optional, Any

import serial # type: ignore
import serial.tools.list_ports
import time

MEGA        = {"device" : "/dev/cu.usbmodem141401", "baud" : 250000, "timeout" : 1}
NANO        = {"device" : "/dev/cu.usbserial-14120", "baud" : 250000, "timeout" : 1}
TERMINAL    = {"device" : "/dev/ttys005", "baud" : 9600, "timeout" : 1}

modem = MEGA

startSym = "-"
endSym = "^"

def getSerialConnection():
    """
    Open a serial connection to the Arduino.
    :return: A serial object
    """
    conn = serial.Serial(modem["device"], modem["baud"], timeout=modem["timeout"])
    time.sleep(3)
#     conn.write('\r'.encode())
#     conn.reset_input_buffer()
#     conn.reset_output_buffer()
    conn.write(startSym.encode()) #put Arduino into ready state
    return conn
       
def write(commands: list[int], conn) -> None:
    """
    Write commands to the Arduino
    :param commands: list[int] - a list of numeric commands: <channel-activation>
    """
    for command in commands:
        commandBytes: bytes = startSym.encode('ascii') + bytes(command) + endSym.encode('ascii')
        numberOfBytesSent: int = conn.write(commandBytes)
    
def read(conn) -> bytes:
    """
    Read data from the Arduino
    :return: bytes - the data that was read.
    """
    data = conn.read_until(expected='\r\n')
    return data

# todo: this should check to see if the arduino is correctly programmed.
def isConnected() -> bool:
    """
    Looks to see if the modem name appears in the list of connected devices.
    NOTE: this only tells you if the cable is connected, not if the connection is up.
    :return: Bool
    """
    ports = [tuple(p)[0] for p in serial.tools.list_ports.comports()]
    if modem['device'] in ports:
        return True
    else:
        return False
