DROP TABLE IF EXISTS devices;

CREATE TABLE devices (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       title TEXT NOT NULL,
       activation BOOL NOT NULL,
       channel INTEGER NOT NULL
);
