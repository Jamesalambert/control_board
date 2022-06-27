from storage import Storage as s
from typing import Optional, Any
import numpy as np

class Feed():
# mark _____________________ state _____________________
    @staticmethod
    def description() -> list[dict[str, Any]]:
        """
        returns a list of dicts, each dicts describes a device. Used for drawing UI 
        """
        deviceList = s.getDeviceStates()
        for d in deviceList:
            if d['id'] in Feed._allowedDeviceIDs():
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
            intent: Optional[str] = Feed._intentFromString(commandData)
        except:
            return None

        if intent == "toggle":
            commands: Optional[list[tuple[int,int]]]
            commands = Feed._getToggleCommandsFor(commandData)
            if not commands is None:
                s.recordActivation(commands)
                return commands
            else:
                return None
        elif intent == "updateChannel":
            deviceID: int
            newChannel: int
            deviceID, newChannel = Feed._getChannelUpdateCommandFor(commandData)
            s.recordChannel(deviceID, newChannel)
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
    def _getToggleCommandsFor(commandData: str) -> Optional[list[tuple[int,int]]]:
        """
        Returns: a list of tuples (d,a) where d is the deviceID and a is the activation i.e. on/off
        """
        deviceID : int
        activation: int
        devicesToToggle: list[int]
        descendants: list[int]
        channels: set[int]
        commands: list[tuple[int,int]]
        
        deviceID = int(commandData.split(",")[1])
        devicesToToggle = [deviceID]
        
        if not deviceID in Feed._allowedDeviceIDs():
            return None
            
        currentActivation: int = s.activationFor(deviceID)
        
        if currentActivation == 0:
#           switch on parents
            activation = 1
            devicesToToggle += Feed._getAncestorDeviceIDs(deviceID)
        else:
#           switch off children too
            activation = 0
            descendants = Feed._getDescendantDeviceIDs(deviceID)
            devicesToToggle += descendants
        
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
    def _intentFromString(data: str) -> Optional[str]:
        try:
            words: list[str] = data.split(",")
            return words[0]
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
        #         will always include the header parentID as the first result, ignore it.
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
        # conn = s._getDBConnection()
#         cur = conn.cursor()
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
        return ancestorIDs[ancestorIDs > 0].tolist()


    @staticmethod
    def _getDescendantDeviceIDs(deviceID: int) -> list[int]:
        """
        returns the children of a given device
        """
        graphRows = s.dependencyGraph()
        deviceIDs: list[int] = [row['parentID'] for row in graphRows]
    
        # row vector
        deviceIDVec = np.array([1 if e == deviceID else 0 for e in deviceIDs])
        graphVec = np.array(list(map(lambda row: [row[k] for k in row.keys() if k != 'parentID'], graphRows)))
    
        descendants = deviceIDVec @ graphVec
        for _ in deviceIDVec:
            descendants |= descendants @ graphVec
        
        descendants = [1 if e > 0 else 0 for e in descendants]
        descendantIDs = np.multiply(deviceIDs, descendants)
        return descendantIDs[descendantIDs > 0].tolist()

#mark add/remove devices ___________________________

    @staticmethod
    def addDevice(title: str):
        s.recordNewDevice(title)
    
    @staticmethod
    def removeDevice(deviceID: int):
        s.removeDevice(deviceID)
