import sqlite3

SQL_SCHEME_FILE = 'schema.sql'

DEVICE_TITLES = ['main power', 'NOX', 'O2', 'alarm', 'beacon', 'ignite']
ACTIVATIONS = [0] * len(DEVICE_TITLES)
CHANNELS = list(range(1, len(DEVICE_TITLES) + 1))

deviceStartData = zip(DEVICE_TITLES, CHANNELS)
outputsStartData = zip(CHANNELS, ACTIVATIONS)

# connection matrix for the device tree
graphStartData = [  [0,0,0,0,1,0],
                    [0,0,0,0,0,0],
                    [0,1,0,0,0,0],
                    [0,0,1,0,0,1],
                    [0,0,0,1,0,0],
                    [0,0,0,0,0,0]]

WARNING = """RUNNING THIS SCRIPT WILL DELETE ANY DEVICES THAT HAVE BEEN ADDED AND RESET CHANNELS TO A DEFAULT STATE.
- Type "reset" to reset the database 
- or type anything else to stop.
"""

answer = input(WARNING)
print(answer)
shouldContinue = answer.strip().lower() == "reset"

if shouldContinue:
    print("resetting...")
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row #python dicts

    with open(SQL_SCHEME_FILE) as f:
        conn.executescript(f.read())

    cur = conn.cursor()
    
    cur.executemany("INSERT INTO devices (title, channel) VALUES (?, ?)", deviceStartData)
    cur.executemany("INSERT INTO outputs (channel, activation) VALUES (?, ?)", outputsStartData)
    
#     columns
    cur.execute("SELECT id from devices")
    deviceIDs = [row['id'] for row in cur.fetchall()]
    for deviceID in deviceIDs:
        cur.execute(f"ALTER TABLE graph ADD COLUMN '{deviceID}' INTEGER DEFAULT 0 NOT NULL")
    
    cur.executemany("INSERT INTO graph VALUES(?,?,?,?,?,?,?)", [[a] + b for a,b in zip(deviceIDs, graphStartData)])
    
    conn.commit()
    conn.close()
else:
    print("stopping.")