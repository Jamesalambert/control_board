import React from 'react';
import {useState, useEffect} from 'react';


function Setup() {

   // new line start
//    useState needs a getter and setter as below and takes an argument for the
//    initial value
  const [devices, setDevices] = useState([]);

// useEffect's second arg is a list of value to watch, it will re-fetch when any of them change.
  useEffect(() => {
    fetch('/setup')
    .then(res => res.json())
    .then(data => {
        if (data){
            setDevices(data);
        }
    })
    .catch((error) => {
        if (error.response){
            console.log(error.response);
        }
    })
  }, []);

  return (
    <div>
        <p>Welcome to control panel</p>
        <p>there are {devices.length} devices.</p>

        {devices.map( (device, _) => {
            return deviceSettings(device);
        })}
    
    </div>
  );
  
  
  function deviceSettings(device) {
    return (
        <div key={device.id} className='deviceSettings'>
            <h2>{device['title']} ({device['id']}) {device['activation'] === 1 ? "✔" : ""}    </h2>
            <p>Channel:</p>
            
                <div className="setChannelButtons">
                {[1,2,3,4,5,6].map( channel => {
                    const cssClass = (channel === device.channel ? 'on' : 'off');
                    return (
                        <button key={channel} className={cssClass}
                        onClick={() => setChannel(device.id, channel)}>{channel}
                        </button>
                    );
                })}
                </div>            
        </div>
    );
    }



    // comms with Flask server
    function setChannel(deviceID, newChannel){
        const command = {intent: 'updateChannel',
                            deviceID: deviceID,
                            newChannel: newChannel}
                            
        return fetch("/setup", {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body:  JSON.stringify(command)
        })
            .then(res => res.json())
            .then(devices => {setDevices(devices);})
    }

}


export default Setup;
