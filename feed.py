# todo: split this into logic + db files

from typing import Optional, Any
from enum import Enum
import sqlite3
import numpy as np

class Feed():
# mark _____________________ state _____________________
    @staticmethod
    def description() -> list[dict[str, Any]]:
        deviceList = Feed._recordChannel()
        for d in deviceList:
            if d['id'] in Feed.__allowedDeviceIDs():
                if d['activation'] == 1:
                    d['cssActivationClass'] = "on"
                else:
                    d['cssActivationClass'] = "off"
            else:
                d['cssActivationClass'] = "disabled"
        return deviceList


#mark _____________________ Command Logic _____________________
    @staticmethod
    def commandsFrom(commandData: str) -> Optional[list[tuple[int,int]]]:
        """
        returned values will be sent to the serial device
        """
        try:
            intent: Optional[str] = Feed.__intentFromString(commandData)
        except:
            return None

        if intent == "toggle":
            commands: Optional[list[tuple[int,int]]]
            commands = Feed.__getToggleCommandsFor(commandData)
            if not commands is None:
                Feed._recordActivation(commands)
                return commands
            else:
                return None
        elif intent == "updateChannel":
            deviceID: int
            newChannel: int
            deviceID, newChannel = Feed.__getChannelUpdateCommandFor(commandData)
            Feed._recordChannel(deviceID, newChannel)
            return None
        else:
            return None
            
        
    @staticmethod
    def commandsFromSerial(data: str):
#     todo: this will receive the repeated commands from the arduino,
#     turn the data into commands, and then commit those commands to the database.
        if len(data) > 0:
            print(f"Feed got serial data: {data}")
        

    @staticmethod
    def __getToggleCommandsFor(commandData: str) -> Optional[list[tuple[int,int]]]:
        deviceID : int
        activation: int
        devicesToToggle: list[int]
        descendants: list[int]
        channels: set[int]
        commands: list[tuple[int,int]]
        
        deviceID = int(commandData.split(",")[1])
        devicesToToggle = [deviceID]
        
        if not deviceID in Feed.__allowedDeviceIDs():
            return None
            
        conn = Feed.__getDBConnection()
        currentActivation: int = Feed.__activationFor(deviceID, conn)
        
        if currentActivation == 0:
#           switch on parents
            activation = 1
            devicesToToggle += Feed.__getAncestorDeviceIDs(deviceID, conn)
        else:
#           switch off children too
            activation = 0
            descendants = Feed.__getDescendantDeviceIDs(deviceID, conn)
            devicesToToggle += descendants
        
        channels = set([Feed.__getChannelFor(deviceID, conn) for deviceID in devicesToToggle])
        conn.close()
        
        commands = [(channel, activation) for channel in channels]
        return commands

 
    @staticmethod
    def __getChannelUpdateCommandFor(commandData: str) -> tuple[int, int]:
        print(f"updating: {commandData}")
        deviceAndChannel = commandData.split(",")
        deviceID: int = int(deviceAndChannel[1])
        newChannel: int = int(deviceAndChannel[2])
        return deviceID, newChannel

    @staticmethod
    def __intentFromString(data: str) -> Optional[str]:
        try:
            words: list[str] = data.split(",")
            return words[0]
        except:
            return None



#MARK  _____________________ device dependency management _____________________
    @staticmethod
    def __allowedDeviceIDs() -> set[int]:
        """
        returns the children of currently active devices
        """
        conn = Feed.__getDBConnection()
        activatedDevicesCommand = """select devices.id from devices, outputs 
where devices.channel = outputs.channel and outputs.activation = 1"""
        cur = conn.cursor()
        activatedDeviceIDsRows = cur.execute(activatedDevicesCommand).fetchall()
        activatedDeviceIDs: list[int] = [row['id'] for row in activatedDeviceIDsRows]
        
        cur = conn.cursor()
        graphRows = cur.execute("select * from graph;").fetchall()
        graphRows = [row for row in graphRows if row['parentID'] in activatedDeviceIDs]
        #         will always include the header parentID as the first result, ignore it.
        enabledDeviceIDs: list[int] = [int(k) for row in graphRows for k in row.keys() if row[k] == 1 and k != 'parentID']
        
        cur = conn.cursor()
        initialDeviceID: list[int] = cur.execute("select id from devices where title = 'main power'").fetchone()
        enabledDeviceIDs += initialDeviceID
        
        conn.close()
        return set(enabledDeviceIDs)


    @staticmethod
    def __getAncestorDeviceIDs(deviceID: int, conn) -> list[int]:
        """
        returns the parents of a given device
        """
        cur = conn.cursor()
        rows = cur.execute("select * from graph").fetchall()
        deviceIDs: list[int] = [row['parentID'] for row in rows]

        # row vector
        deviceIDVec = np.array([1 if e == deviceID else 0 for e in deviceIDs])
        graphVec = np.array(list(map(lambda row: [row[k] for k in row.keys() if k != 'parentID'], rows)))

        ancestors = graphVec @ deviceIDVec
        for _ in deviceIDVec:
            ancestors |= graphVec @ ancestors

        ancestors = [1 if e > 0 else 0 for e in ancestors]
        ancestorIDs = np.multiply(deviceIDs, ancestors)
        return ancestorIDs[ancestorIDs > 0].tolist()


    @staticmethod
    def __getDescendantDeviceIDs(deviceID: int, conn) -> list[int]:
        """
        returns the children of a given device
        """
        cur = conn.cursor()
        rows = cur.execute("select * from graph").fetchall()
        deviceIDs: list[int] = [row['parentID'] for row in rows]
    
        # row vector
        deviceIDVec = np.array([1 if e == deviceID else 0 for e in deviceIDs])
        graphVec = np.array(list(map(lambda row: [row[k] for k in row.keys() if k != 'parentID'], rows)))
    
        descendants = deviceIDVec @ graphVec
        for _ in deviceIDVec:
            descendants |= descendants @ graphVec
        
        descendants = [1 if e > 0 else 0 for e in descendants]
        descendantIDs = np.multiply(deviceIDs, descendants)
        return descendantIDs[descendantIDs > 0].tolist()




#MARK _____________________ Database actions _____________________
# TODO: adding a new device also needs to add it to the graph
    @staticmethod
    def recordNewDevice(title: str):
        conn = Feed.__getDBConnection()
        Feed.__addDevice(title, conn)
        conn.commit()
        conn.close()
        
    @staticmethod
    def removeDevice(deviceID: int):
        conn = Feed.__getDBConnection()
        Feed.__deleteDevice(deviceID, conn)
        conn.commit()
        conn.close()
        
    @staticmethod
    def _recordActivation(commands: list[tuple[int, int]]):
        conn = Feed.__getDBConnection()

        for channel, activation in commands:
            Feed.__setActivation(activation, channel, conn)
            
        conn.commit()
        conn.close()

    @staticmethod
    def _recordChannel(deviceID: int, newChannel: int):
        conn = Feed.__getDBConnection()
        Feed.__setChannel(deviceID, newChannel, conn)
        conn.commit()
        conn.close()

    @staticmethod
    def _recordChannel() -> list[dict[str, Any]]:
        """
        returns all device activations
        """
        conn = Feed.__getDBConnection()
        cur = conn.cursor()
        cur.execute("select * from devices LEFT JOIN outputs ON devices.channel = outputs.channel;")
        deviceStates = [dict(row) for row in cur]
        conn.close()
        return deviceStates
        

#MARK _____________________ db access helpers_____________________

    @staticmethod
    def __getDBConnection():
        conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row #python dicts
        return conn

    @staticmethod
    def __activationFor(deviceID: int, conn) -> int:
        command = """
select activation
from devices, outputs
where devices.channel = outputs.channel
and devices.id = ?;
"""
        activations = conn.execute(command, str(deviceID)).fetchone()
        print(f"db got activation: {activations['activation']}")
        return activations['activation']

    @staticmethod
    def __setActivation(activation: int, channel: int, conn):
        command = "update outputs set activation = ? where channel = ?;"
        conn.execute(command, [str(activation), str(channel)])
        print(f"updating database: {activation} for channel: {channel}")
        
    @staticmethod
    def __getChannelFor(deviceID: int, conn) -> int:
        command = "select channel from devices where id = ?"
        row = conn.execute(command, (str(deviceID),)).fetchone()
        return row['channel']
        
    @staticmethod
    def __setChannel(deviceID: int, newChannel: int, conn):
        conn.execute("UPDATE devices set channel = ? WHERE id is ?", (str(newChannel), str(deviceID)))
        print(f"updated db, set device {deviceID} to channel: {newChannel}")
        
    @staticmethod
    def __addDevice(title: str, conn):
        conn.execute("INSERT INTO devices (title) VALUES (?)", (title,))
        print(f"updating database: added {title}")
        
    @staticmethod
    def __deleteDevice(deviceID: int, conn):
        conn.execute("DELETE FROM devices WHERE id = ?", (str(deviceID),))
        print(f"deleted device {deviceID}")
        
    