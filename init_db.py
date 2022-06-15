import sqlite3

SQL_SCHEME_FILE = 'schema.sql'
DEVICE_TITLES = ['main power', 'NOX', 'O2', 'alarm', 'beacon', 'ignite']
ACTIVATIONS = [0] * len(DEVICE_TITLES)
CHANNELS = list(range(1, len(DEVICE_TITLES) + 1))

deviceStartData = zip(DEVICE_TITLES, CHANNELS)
outputsStartData = zip(CHANNELS, ACTIVATIONS)

WARNING = """RUNNING THIS SCRIPT WILL DELETE ANY DEVICES THAT HAVE BEEN ADDED AND RESET CHANNELS TO A DEFAULT STATE.
Type reset to reset the database.
Type anything else and the press enter to stop.           
"""


answer = raw_input(WARNING)
print(answer)
shouldContinue = answer.strip().lower() == "reset"

if shouldContinue:
    print("resetting...")
    conn = sqlite3.connect('database.db')

    with open(SQL_SCHEME_FILE) as f:
        conn.executescript(f.read())

    cur = conn.cursor()
    cur.executemany("INSERT INTO devices (title, channel) VALUES (?, ?)", deviceStartData)
    cur.executemany("INSERT INTO outputs (channel, activation) VALUES (?, ?)", outputsStartData)
    conn.commit()
    conn.close()
else:
    print("stopping.")