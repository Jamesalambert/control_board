var messageBoard = document.getElementById('messageBoard');
var body = document.getElementById('tree');


socket.addEventListener('message', ev => {
        const rootDeviceData = JSON.parse(ev.data);  
        if (typeof(rootDeviceData) == 'object' && 'children' in rootDeviceData){
            body.innerHTML = controlFor(rootDeviceData);
        }
});


function toggle(deviceID) {
    socket.send("toggle," + deviceID);
}


function controlFor(device){
    const buttonHTML = `<button id='${device.id}' class='${device.cssActivationClass}' onclick='toggle(${device.id})'> ${device.title}</button>`;
    var childrenDiv = "";

    if (device.children.length > 0) {
        var childrenHTML = "";
        for (const childDevice of device['children']){
            childrenHTML += controlFor(childDevice);
        }
        childrenDiv = `<div class='deviceChildren'>${childrenHTML}</div>`;
    } 
    const divHTML = `<div class='device'>${buttonHTML}  ${childrenDiv}</div>`;
    return divHTML;
}