from enum import Enum
import sqlite3

class Device(Enum):
    POWER   = 1
    NOX     = 2
    O2      = 3
    ALARM   = 4
    BEACON  = 5
    IGNITE  = 6

class FeedState(Enum):
    SAFE    = {Device.POWER}
    ARMED   = set(Device)

class Feed():
# =============Public==================
# State _______________________________
    @staticmethod
    def description():
        deviceList = Feed.__getDeviceStates()
        for d in deviceList:
            if d['id'] in Feed.__allowedDeviceIDs():
                if d['activation'] == 1:
                    d['cssActivationClass'] = "on"
                else:
                    d['cssActivationClass'] = "off"
            else:
                d['cssActivationClass'] = "disabled"
        return deviceList

    @staticmethod
    def state():
        devList = Feed.__getDeviceStates()
        powerOn = [d['activation'] == 1 for d in devList if d['title'] == 'main power'][0]
        if powerOn:
            return FeedState.ARMED
        else:
            return FeedState.SAFE

    @staticmethod
    def __allowedDeviceIDs():
        return {e.value for e in Feed.state().value}

    @staticmethod
    def commandsFromSerial(data):
#     todo: this will receive the repeated commands from the arduino,
#     turn the data into commands, and then commit those commands to the database.
        if len(data) > 0:
            print(f"Feed got serial data: {data}")

# Command logic ____________________________
    @staticmethod
    def commandFrom(commandData):
        """
        returned values will be sent to the serial device
        """
        try:
            intent = Feed.__intentFromString(commandData)
        except:
            return None
            
        if intent == "toggle":
            command = Feed.__getToggleCommandFor(commandData)
            if not command == None:
                Feed.__recordActivation(*command)
                return command
            else:
                return None
        elif intent == "updateChannel":
            command = Feed.__getChannelUpdateCommandFor(commandData)
            Feed.__recordChannel(*command)
            return None
        else:
            return None

#  =================Private==================     
    @staticmethod
    def __getToggleCommandFor(commandData):
        deviceID = commandData.split(",")[1]
        if not int(deviceID) in Feed.__allowedDeviceIDs():
            return None

        conn = Feed.__getDBConnection()

        channel = Feed.__getChannelFor(deviceID, conn)
        currentActivation = Feed.__activationFor(deviceID, conn)

        if currentActivation == 0:
            activation = 1
        else:
            activation = 0

        conn.close()
        return channel, activation

    @staticmethod
    def __getChannelUpdateCommandFor(commandData):
        deviceID, newChannel = commandData.split(",")[1:3]
        return deviceID, newChannel

    @staticmethod
    def __intentFromString(data):
        try:
            data = data.split(",")
            return data[0]
        except:
            return None

# Database actions ___________________________
    @staticmethod
    def __recordActivation(channel, activation):
        conn = Feed.__getDBConnection()
        Feed.__setActivation(activation, channel, conn)
        conn.commit()
        conn.close()

    @staticmethod
    def __recordChannel(deviceID, newChannel):
        conn = Feed.__getDBConnection()
        Feed.__setChannel(deviceID, newChannel, conn)
        conn.commit()
        conn.close()
        
    @staticmethod
    def recordNewDevice(title):
        conn = Feed.__getDBConnection()
        Feed.__addDevice(title, conn)
        conn.commit()
        conn.close()
        
    @staticmethod
    def removeDevice(deviceID):
        conn = Feed.__getDBConnection()
        Feed.__deleteDevice(deviceID, conn)
        conn.commit()
        conn.close()

# Private ---------------------
    @staticmethod
    def __getDBConnection():
        conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row #python dicts
        return conn
        
    @staticmethod
    def __getDeviceStates():
        conn = Feed.__getDBConnection()
        cur = conn.cursor()
        cur.execute("select * from devices LEFT JOIN outputs ON devices.channel = outputs.channel;")
        deviceStates = [dict(row) for row in cur]
        conn.close()
        return deviceStates
        
    @staticmethod
    def __getChannelFor(deviceID, conn):
        command = "select channel from devices where id = ?"
        row = conn.execute(command, deviceID).fetchone()
        return row['channel']

    @staticmethod
    def __activationFor(deviceID, conn):
        command = """
select activation
from devices, outputs
where devices.channel = outputs.channel
and devices.id = ?;
"""
        activations = conn.execute(command, deviceID).fetchone()
        print(f"db got activation: {activations['activation']}")
        return activations['activation']

    @staticmethod
    def __setActivation(activation, channel, conn):
        command = "update outputs set activation = ? where channel = ?;"
        conn.execute(command, [str(activation), str(channel)])
        print(f"updating database: {activation} for channel: {channel}")
        
    @staticmethod
    def __setChannel(deviceID, newChannel, conn):
        conn.execute("UPDATE devices set channel = ? WHERE id is ?", (newChannel, deviceID))
        print(f"updated db, set device {deviceID} to channel: {newChannel}")
        
    @staticmethod
    def __addDevice(title, conn):
        conn.execute("INSERT INTO devices (title) VALUES (?)", (title,))
        print(f"updating database: added {title}")
        
    @staticmethod
    def __deleteDevice(deviceID, conn):
        conn.execute("DELETE FROM devices WHERE id = ?", (deviceID,))
        print(f"deleted device {deviceID}")
        
    