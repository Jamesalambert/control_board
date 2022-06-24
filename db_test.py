import sqlite3
 
def __getDBConnection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row #python dicts
    return conn
 
def __getParentDeviceIDs(deviceID, conn):
    cur = conn.cursor()
    rows = cur.execute(f'select parentID from graph where "{deviceID}"').fetchall()
    return [row['parentID'] for row in rows]
    
def __getChildrenDeviceIDs(deviceID, conn):
    cur = conn.cursor()
    rows = cur.execute("select * from graph where parentID = ?", (deviceID,)).fetchall()
    children = [int(k) for row in rows for k in row.keys() if row[k] == 1 and k!= 'parentID']
    return children
    
    
conn = __getDBConnection()

for deviceID in range(1,6):
    print(f"device: {deviceID}")
    print(f"children: {__getChildrenDeviceIDs(deviceID, conn)}")
    print(f"parents: {__getParentDeviceIDs(deviceID, conn)}")