# Control Panel

This presents a React web interface to control devices via an Arduino.

Communication takes place over the serial port.

The state of the hardware is stored in a Sqlite3 database

# Installation

1. `cd control_planel`
1. `pip install -r requirements.txt`
1. `cd flask_react`
1. `npm install`


# usage
`npm run start-app`

this will run the react front end and start the flask/SQL backend