# Control Panel

This presents a React web interface to control devices via an Arduino.

Communication takes place over the serial port.

The state of the hardware is stored in a Sqlite3 database

# Requirements
1. Python 3.9+
1. Node.js 10.19+


# Installing Node
1. Install nvm (https://github.com/nvm-sh/nvm#installing-and-updating)
1. `nvm install --lts`

# Installation
1. `cd control_board`
1. `pip install -r requirements.txt`
1. `cd flask_react`
1. `npm install`

# Usage
1. `cd flask_react`
1. `npm run start-app`

this will run the react front end and start the flask/SQL backend.