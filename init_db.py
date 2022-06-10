import sqlite3

DEVICE_TITLES = ['main power', 'NOX', 'O2', 'alarm', 'beacon', 'ignite']
startData = zip(DEVICE_TITLES, [0] * len(DEVICE_TITLES))

connection = sqlite3.connect('database.db')

with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

cur.executemany("INSERT INTO devices (title, activation) VALUES (?, ?)", startData)

connection.commit()
connection.close()
