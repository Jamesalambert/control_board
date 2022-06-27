from typing import Optional, Any
import sqlite3


class Storage():

#MARK Public:_____ Database actions _____________________
# TODO: adding a new device also needs to add it to the graph
    @staticmethod
    def recordNewDevice(title: str):
        conn = Storage._getDBConnection()
        Storage.__addDevice(title, conn)
        conn.commit()
        conn.close()
        
    @staticmethod
    def removeDevice(deviceID: int):
        conn = Storage._getDBConnection()
        Storage.__deleteDevice(deviceID, conn)
        conn.commit()
        conn.close()
        
    @staticmethod
    def recordActivation(commands: list[tuple[int, int]]):
        conn = Storage._getDBConnection()

        for channel, activation in commands:
            Storage.__setActivation(activation, channel, conn)
            
        conn.commit()
        conn.close()
        
    @staticmethod
    def activationFor(deviceID: int) -> int:
        conn = Storage._getDBConnection()
        activation: int = Storage.__activationFor(deviceID, conn)
        conn.close()
        return activation

    @staticmethod
    def recordChannel(deviceID: int, newChannel: int):
        conn = Storage._getDBConnection()
        Storage.__setChannel(deviceID, newChannel, conn)
        conn.commit()
        conn.close()

    @staticmethod 
    def channelFor(deviceID: int) -> int:
        conn = Storage._getDBConnection()
        channel = Storage.__getChannelFor(deviceID, conn)
        conn.close()
        return channel

    @staticmethod
    def getDeviceStates() -> list[dict[str, Any]]:
        """
        returns all device information including activations.
        """
        conn = Storage._getDBConnection()
        cur = conn.cursor()
        cur.execute("select * from devices LEFT JOIN outputs ON devices.channel = outputs.channel;")
        deviceStates = [dict(row) for row in cur]
        conn.close()
        return deviceStates
        
    @staticmethod
    def dependencyGraph() -> list[dict[str, Any]]:
        conn = Storage._getDBConnection()
        cur = conn.cursor()
        graph = cur.execute("select * from graph").fetchall()
        conn.close()
        return graph
        
    @staticmethod
    def rootDevice() -> int:
        conn = Storage._getDBConnection()
        cur = conn.cursor()
        initialDeviceID: list[int] = cur.execute("select id from devices where title = 'main power'").fetchone()
        return initialDeviceID[0]

        

#MARK Private:______ db access helpers_____________________

    @staticmethod
    def _getDBConnection():
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
        
    