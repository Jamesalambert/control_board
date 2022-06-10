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
# State _______________________________
    @staticmethod
    def description():
        deviceList = Feed.__getDeviceStates()
        for d in deviceList:
            if d['id'] in Feed.allowedDeviceIDs():
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
    
    
        

# Command logic ____________________________
    @staticmethod
    def commandFrom(data):
        try:
            intent, deviceID = Feed.__intentFromString(data)
        except:
            return None
        if intent == "toggle":
            command = Feed.getToggleCommandFor(deviceID)
#             temporary______________
            Feed.updateDB(*command)
#             remove!!!!!
            return command
        else:
            return None
            
    @staticmethod
    def getToggleCommandFor(deviceID):
        if not deviceID in Feed.allowedDeviceIDs():
            return
        
        conn = Feed.__getDBConnection()
        currentActivation = Feed.__activationFor(deviceID, conn)
        if currentActivation == 0:
            activation = 1
        else:
            activation = 0
        return deviceID, activation
            
    @staticmethod
    def allowedDeviceIDs():
        return {e.value for e in Feed.state().value}
    
    @staticmethod
    def __intentFromString(data):
        try:
            data = data.split(",")[:2]
            return (data[0], int(data[1]))
        except:
            return None
        
    
# Database actions ___________________________
    @staticmethod
    def toggle(deviceID):
        conn = Feed.__getDBConnection()
        
        currentActivation = Feed.__activationFor(deviceID, conn)
        if currentActivation == 0 :
            Feed.__setActivation(1, deviceID, conn)
        else:
            Feed.__setActivation(0, deviceID, conn)

        conn.commit()
        conn.close() 

    # @staticmethod
#     def synchroniseDevicesToDB():
#         deviceStates = Feed.__getDeviceStates()
#         for deviceData in deviceStates:
#             Hardware.setActivation(deviceData['activation'], deviceData['id'])
#         return

    @staticmethod
    def updateDB(deviceID, activation):
        conn = Feed.__getDBConnection()
        Feed.__setActivation(activation, deviceID, conn)
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
        cur.execute('select * from devices')
        deviceStates = [dict(row) for row in cur]
        conn.close()
        return deviceStates

    @staticmethod
    def __activationFor(deviceID, conn):
        row = conn.execute(f"select * from devices where id is {deviceID}").fetchone()
        return row['activation']
    
    @staticmethod
    def __setActivation(activation, deviceID, conn):
        conn.execute(f'UPDATE devices SET activation = {activation} WHERE id is {deviceID}')
        print(f"updating database: {activation} for device {deviceID}")


