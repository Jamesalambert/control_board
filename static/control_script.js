socket.addEventListener('message', ev => {
        const devices = JSON.parse(ev.data);
        
        for (const device of devices){
//             messageBoard.innerHTML += JSON.stringify(device);
            $('#' + device['id']).attr('class', device['cssActivationClass']);
        }
});

function toggle(deviceID) {
    socket.send("toggle," + deviceID);
}