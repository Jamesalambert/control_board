import sqlite3
import numpy as np

def __getDBConnection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row #python dicts
    return conn



def __getAncestorDeviceIDs(deviceID, conn):
    """
    returns the parents of a given device
    """
    cur = conn.cursor()
    rows = cur.execute("select * from graph").fetchall()
    deviceIDs = [row['parentID'] for row in rows]
    
    # row vector
    deviceIDVec = np.array([1 if e == deviceID else 0 for e in deviceIDs])
    graphVec = np.array(list(map(lambda row: [row[k] for k in row.keys() if k != 'parentID'], rows)))
    
    ancestors = graphVec @ deviceIDVec
    for _ in deviceIDVec:
        ancestors |= graphVec @ ancestors
    
    ancestors = [1 if e > 0 else 0 for e in ancestors]
    ancestorIDs = np.multiply(deviceIDs, ancestors)
    return ancestorIDs[ancestorIDs > 0].tolist()


def __getDescendantDeviceIDs(deviceID, conn):
    """
    returns the children of a given device
    """
    cur = conn.cursor()
    rows = cur.execute("select * from graph").fetchall()
    deviceIDs = [row['parentID'] for row in rows]
    
    # row vector
    deviceIDVec = np.array([1 if e == deviceID else 0 for e in deviceIDs])
    graphVec = np.array(list(map(lambda row: [row[k] for k in row.keys() if k != 'parentID'], rows)))
    
    descendants = deviceIDVec @ graphVec
    for _ in deviceIDVec:
        descendants |= descendants @ graphVec
        
    descendants = [1 if e > 0 else 0 for e in descendants]
    descentantIDs = np.multiply(deviceIDs, descendants)
    return descentantIDs[descentantIDs > 0].tolist()
    
    
    
    
conn = __getDBConnection()

for deviceID in range(1,7):
    print(deviceID)
    print(f"children: {__getDescendantDeviceIDs(deviceID, conn)}")
    print(f"parents: {__getAncestorDeviceIDs(deviceID, conn)}")
    
