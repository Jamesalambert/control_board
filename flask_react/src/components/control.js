import React from 'react';
import {useState, useEffect} from 'react';
import '../index.css'

function Control() {

   // new line start
//    useState needs a getter and setter as below and takes an argument for the
//    initial value
  const [rootDevice, setRootDevice] = useState({});

// useEffect's second arg is a list of value to watch, it will re-fetch when any of them change.
  useEffect(() => {
    fetch('/hierarchy')
    .then(res => res.json())
    .then(data => {
        if (data){
            setRootDevice(data);
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
        {controlFor(rootDevice)}
    </div>
    );


    function controlFor(device){
        return (
            <div className="device">
                <button id={device.id} className={device.cssActivationClass} onClick={() => toggle(device.id)}>
                    {device.title}
                </button>
                     { 'children' in device ?
                         device.children.map((childDevice) => {
                             return (controlFor(childDevice));
                         }) : ""
                     }
            </div>
        );
    }
  
  
    // comms with Flask server
    function toggle(deviceID){
        const command = {intent: 'toggle',
                            deviceID: deviceID}
                            
        return fetch("/hierarchy", {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body:  JSON.stringify(command)
        })
            .then(res => res.json())
            .then(device => {setRootDevice(device);})
    }
  
 
}


export default Control;
