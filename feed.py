from storage import Storage as s
from typing import Optional, Any
import numpy as np
import json


class Feed():
# mark _____________________ state _____________________
    @staticmethod
    def description() -> list[dict[str, Any]]:
        """
        returns a list of dicts, each dicts describes a device. Used for drawing UI 
        """
        deviceList = s.getDeviceStates()
        for d in deviceList:
            d['children'] = Feed._getDescendantDeviceIDs(d['id'], 1)
            if d['id'] in Feed._allowedDeviceIDs():
                if d['activation'] == 1:
                    d['cssActivationClass'] = "on"
                else:
                    d['cssActivationClass'] = "off"
            else:
                d['cssActivationClass'] = "disabled"
        return deviceList


    @staticmethod
    def tree() -> str:
        deviceList: list[dict[str, Any]]
        deviceList = Feed.description()

        for d in deviceList:
            d['children'] = Feed._getDescendantDeviceIDs(d['id'], depth=1)

        for device in deviceList:
            childDevices: list[dict[str, Any]] = []
            for childID in device['children']:
                childDevice = next(filter(lambda d: d['id'] == childID, deviceList))
                childDevices.append(childDevice)
            
            device['children'] = childDevices

        rootDevice: dict[str,Any]
        rootDevice = next(filter(lambda d: d['id'] == s.rootDevice(), deviceList))
        jsonDescription: str = json.dumps(rootDevice)
        return jsonDescription



    @staticmethod
    def deviceFromID(deviceStates, deviceID):
        return next(filter(lambda device: device['id'] == deviceID, deviceStates))

#mark _____________________ Command Logic _____________________
    @staticmethod
    def commandsFrom(commandData: str) -> Optional[list[tuple[int,int]]]:
        """
        returned values will be sent to the serial device
        """
        try:
            command: Optional[dict] = Feed._commandFromString(commandData)
        except:
            return None

        if command['intent'] == "toggle":
            commands: Optional[list[tuple[int,int]]]
            commands = Feed._getToggleCommandsFor(command)
            if not commands is None:
                s.recordActivation(commands)
                return commands
            else:
                return None
        elif command['intent'] == "updateChannel":
            deviceID: int = command['deviceID']
            newChannel: int = command['newChannel']
            s.recordChannel(deviceID, newChannel)
            return None
        elif command['intent'] == "addDevice":
            deviceTitle: str = commandData[1]
            return None
        elif command['intent'] == "removeDevice":
            deviceID: int = int(commandData[1])
            s.removeDevice(deviceID)
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
    def _getToggleCommandsFor(command: dict) -> Optional[list[tuple[int,int]]]:
        """
        Returns: a list of tuples (d,a) where d is the deviceID and a is the activation i.e. on/off
        """
        deviceID : int
        activation: int
        devicesToToggle: set[Any]
        channels: set[int]
        commands: list[tuple[int,int]]
        
        deviceID = command['deviceID']
        devicesToToggle = {deviceID}
        
        if not deviceID in Feed._allowedDeviceIDs():
            return None
            
        currentActivation: int = s.activationFor(deviceID)
        
        if currentActivation == 0:
#           switch on parents
            activation = 1
            devicesToToggle = devicesToToggle.union(Feed._getAncestorDeviceIDs(deviceID))
        else:
#           switch off children too
            activation = 0
            devicesToToggle = devicesToToggle.union(Feed._getDescendantDeviceIDs(deviceID))
        
        channels = set([s.channelFor(deviceID) for deviceID in devicesToToggle])
        
        commands = [(channel, activation) for channel in channels]
        return commands

 
    @staticmethod
    def _getChannelUpdateCommandFor(commandData: str) -> tuple[int, int]:
        print(f"updating: {commandData}")
        deviceAndChannel = commandData.split(",")
        deviceID: int = int(deviceAndChannel[1])
        newChannel: int = int(deviceAndChannel[2])
        return deviceID, newChannel

    @staticmethod
    def _commandFromString(data: str) -> Optional[dict]:
        try:
            command: dict = json.loads(data)
            return command
        except:
            return None


#MARK  _____________________ device dependency management _____________________
    @staticmethod
    def _allowedDeviceIDs() -> set[int]:
        """
        returns the children of currently active devices
        """
#       get devices that are currently on
        deviceStates: list[dict[str, Any]]
        deviceStates = s.getDeviceStates()
        activatedDeviceIDs: list[int] = [row['id'] for row in deviceStates if row['activation'] == 1]

#       get their immediate children
        graphRows: list[dict[str, Any]]
        graphRows = s.dependencyGraph()
        graphRows = [row for row in graphRows if row['parentID'] in activatedDeviceIDs]
#       will always include the header parentID as the first result, ignore it.
        enabledDeviceIDs: list[int] = [int(k) for row in graphRows for k in row.keys() if row[k] == 1 and k != 'parentID']

#       always include the 'start' device
        initialDeviceID: int = s.rootDevice()
        enabledDeviceIDs.append(initialDeviceID)

        return set(enabledDeviceIDs)
        

    @staticmethod
    def _getAncestorDeviceIDs(deviceID: int) -> list[int]:
        """
        returns the parents of a given device
        """
        graphRows = s.dependencyGraph()
        deviceIDs: list[int] = [row['parentID'] for row in graphRows]

        # row vector
        deviceIDVec = np.array([1 if e == deviceID else 0 for e in deviceIDs])
        graphVec = np.array(list(map(lambda row: [row[k] for k in row.keys() if k != 'parentID'], graphRows)))

        ancestors = graphVec @ deviceIDVec
        for _ in deviceIDVec:
            ancestors |= graphVec @ ancestors

        ancestors = [1 if e > 0 else 0 for e in ancestors]
        ancestorIDs = np.multiply(deviceIDs, ancestors)
        ancestorIDs = ancestorIDs[ancestorIDs > 0]
        return np.unique(ancestorIDs).tolist()


    @staticmethod
    def _getDescendantDeviceIDs(deviceID: int, depth: int = None) -> list[int]:
        """
        returns the children of a given device
        """
        graphRows = s.dependencyGraph()
        deviceIDs: list[int] = [row['parentID'] for row in graphRows]
    
        # row vector
        deviceIDVec = np.array([1 if e == deviceID else 0 for e in deviceIDs])
        graphVec = np.array(list(map(lambda row: [row[k] for k in row.keys() if k != 'parentID'], graphRows)))
        descendants = deviceIDVec @ graphVec

        depth = len(deviceIDVec) if depth is None else abs(depth)
        
        if depth > 1:
            for _ in range(depth):
                descendants |= descendants @ graphVec
        
        descendants = [1 if e > 0 else 0 for e in descendants]
        descendantIDs = np.multiply(deviceIDs, descendants)
        descendantIDs = descendantIDs[descendantIDs > 0]
        output = np.unique(descendantIDs).tolist()
        return output

#mark add/remove devices ___________________________
    @staticmethod
    def addDevice(title: str) -> None:
        s.recordNewDevice(title)
    
    @staticmethod
    def removeDevice(deviceID: int) -> None:
        s.removeDevice(deviceID)

    @staticmethod
    def updateChannel(deviceID: int, newChannel: int):
        s.recordChannel(deviceID, newChannel)

