from enum import Enum
import sqlite3

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
            commands = Feed.__getToggleCommandsFor(commandData)
            if commands != None:
                Feed.__recordActivation(commands)
                return commands
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
    def __getToggleCommandsFor(commandData):
        deviceID = commandData.split(",")[1]
        
        if not int(deviceID) in Feed.__allowedDeviceIDs():
            return None

        conn = Feed.__getDBConnection()
        currentActivation = Feed.__activationFor(deviceID, conn)
        
        devicesToToggle = [deviceID]
        if currentActivation == 0:
            activation = 1
#             switch on parents
            devicesToToggle += Feed.__getParentDeviceIDs(deviceID, conn)
        else:
            activation = 0
#             switch off children too
            devicesToToggle += Feed.__getChildrenDeviceIDs(deviceID, conn)
        
        channels = set([Feed.__getChannelFor(deviceID, conn) for deviceID in devicesToToggle])
        conn.close()

        commands = [(channel, activation) for channel in channels]
#         TODO remove the [0] below
        return commands

 
    

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
    def __recordActivation(commands):
        conn = Feed.__getDBConnection()

        for channel, activation in commands:
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
        """
        returns all device activations
        """
        conn = Feed.__getDBConnection()
        cur = conn.cursor()
        cur.execute("select * from devices LEFT JOIN outputs ON devices.channel = outputs.channel;")
        deviceStates = [dict(row) for row in cur]
        conn.close()
        return deviceStates
    
    @staticmethod
    def __allowedDeviceIDs():
        """
        returns the children of currently active devices
        """
        conn = Feed.__getDBConnection()
        activatedDevicesCommand = """select devices.id from devices, outputs 
where devices.channel = outputs.channel and outputs.activation = 1"""
        cur = conn.cursor()
        activatedDeviceIDsRows = cur.execute(activatedDevicesCommand).fetchall()
        activatedDeviceIDs = [row['id'] for row in activatedDeviceIDsRows]
        
        cur = conn.cursor()
        graphRows = cur.execute("select * from graph;").fetchall()
        graphRows = [row for row in graphRows if row['parentID'] in activatedDeviceIDs]
        #         will always include the header parentID as the first result, ignore it.
        enabledDeviceIDs = [int(k) for row in graphRows for k in row.keys() if row[k] == 1 and k != 'parentID']
        
        cur = conn.cursor()
        initialDeviceID = cur.execute("select id from devices where title = 'main power'").fetchone()
        enabledDeviceIDs += initialDeviceID
        print(f"enabled: {enabledDeviceIDs}")
        
        conn.close()
        return enabledDeviceIDs
        
    @staticmethod
    def __requiredDeviceIDs():
        """
        returns all parents of currently active devices
        """
    
        conn = Feed.__getDBConnection()
        cur = conn.cursor()
    
        activeDeviceIDCommand = "select devices.id from devices, outputs where devices.channel = outputs.channel and outputs.activation = 1"
        rows = cur.execute(activeDeviceIDCommand).fetchall()
        activeDeviceIDs = [row['id'] for row in rows]
    
        requiredDeviceIDs = []
        for deviceID in activeDeviceIDs:
            rows = cur.execute(f"select parentID from graph where '{deviceID}' == 1").fetchall()
            requiredDeviceIDs += [row['parentID'] for row in rows]
        print(f"required: {requiredDeviceIDs}")
        conn.close()
        return requiredDeviceIDs
    
    @staticmethod
    def __getParentDeviceIDs(deviceID, conn):
#     TODO needs to be recursive
        """
        returns the parents of a given device
        """
        cur = conn.cursor()
        rows = cur.execute(f'select parentID from graph where "{deviceID}"').fetchall()
        return [row['parentID'] for row in rows]
    
    @staticmethod
    def __getChildrenDeviceIDs(deviceID, conn):
#     TODO needs to be recursive
        """
        returns the children of a given device
        """
        cur = conn.cursor()
        rows = cur.execute("select * from graph where parentID = ?", (deviceID,)).fetchall()
        children = [int(k) for row in rows for k in row.keys() if row[k] == 1 and k!= 'parentID']
        return children
    
    @staticmethod
    def __getChannelFor(deviceID, conn):
        command = "select channel from devices where id = ?"
        row = conn.execute(command, (deviceID,)).fetchone()
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
        
    