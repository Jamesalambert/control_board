from typing import Optional, Any
from pathlib import Path
import sqlite3


class Storage():
    dbFileName: str = 'database.db'
    dbPath = Path(__file__).parents[0] / dbFileName

#MARK Public:_____ Database actions _____________________
# TODO: adding a new device also needs to add it to the graph
    @staticmethod
    def recordNewDevice(title: str) -> None:
        conn = Storage._getDBConnection()
        Storage.__addDevice(title, conn)
        conn.commit()
        conn.close()
        
    @staticmethod
    def removeDevice(deviceID: int)  -> None:
        conn = Storage._getDBConnection()
        Storage.__deleteDevice(deviceID, conn)
        conn.commit()
        conn.close()
        
    @staticmethod
    def recordActivation(commands: list[tuple[int, int]]) -> None:
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
    def recordChannel(deviceID: int, newChannel: int) -> None:
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
        :return: list[dict[str, Any]] -  All device information including activations.
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
        """
        :return: sqlite3 database connection 
        """
        conn = sqlite3.connect(Storage.dbPath)
        conn.row_factory = sqlite3.Row #python dicts
        return conn

    @staticmethod
    def __activationFor(deviceID: int, conn) -> int:
        """
        Find out whether a device is on or off
        :param deviceID: Int - device id
        :param conn: sqlite db connection
        :return: int - activation of the device
        """
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
    def __setActivation(activation: int, channel: int, conn) -> None:
        """
        Set the activation for a device
        :param deviceID: Int - device id
        :param conn: sqlite db connection
        """
        command = "update outputs set activation = ? where channel = ?;"
        conn.execute(command, [str(activation), str(channel)])
        print(f"updating database: {activation} for channel: {channel}")

    @staticmethod
    def __getChannelFor(deviceID: int, conn) -> int:
        """
        Get a device's channel number
        :param deviceID: Int - device id
        :param conn: sqlite db connection
        :return: int - device's channel
        """
        command = "select channel from devices where id = ?"
        row = conn.execute(command, (str(deviceID),)).fetchone()
        return row['channel']
        
    @staticmethod
    def __setChannel(deviceID: int, newChannel: int, conn)  -> None:
        """
        Set a device's channel number
        :param deviceID: Int - device id
        :param conn: sqlite db connection
        """
        conn.execute("UPDATE devices set channel = ? WHERE id is ?", (str(newChannel), str(deviceID)))
        print(f"updated db, set device {deviceID} to channel: {newChannel}")
        
    @staticmethod
    def __addDevice(title: str, conn)  -> None:
        """
        Add a device to the database
        :param title: str - device name
        :param conn: sqlite db connection
        """
        conn.execute("INSERT INTO devices (title) VALUES (?)", (title,))
        print(f"updating database: added {title}")
        
    @staticmethod
    def __deleteDevice(deviceID: int, conn)  -> None:
        """
        Delete a device from the database
        :param deviceID: int - device id
        :param conn: sqlite db connection
        """
        conn.execute("DELETE FROM devices WHERE id = ?", (str(deviceID),))
        print(f"deleted device {deviceID}")
        
    