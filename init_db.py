import sqlite3

DEVICE_TITLES = ['main power', 'NOX', 'O2', 'alarm', 'beacon', 'ignite']
ACTIVATIONS = [0] * len(DEVICE_TITLES)
CHANNELS = list(range(len(DEVICE_TITLES)))

startData = zip(DEVICE_TITLES, ACTIVATIONS, CHANNELS)

connection = sqlite3.connect('database.db')

with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

cur.executemany("INSERT INTO devices (title, activation, channel) VALUES (?, ?, ?)", startData)

connection.commit()
connection.close()
