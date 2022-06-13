socket.addEventListener('message', ev => {
        const devices = JSON.parse(ev.data);
        
        for (const device of devices){
//             messageBoard.innerHTML += JSON.stringify(device);
            $('#' + device['id']).attr('class', device['cssActivationClass']);
        }
});



function updateChannel(deviceID, newChannel){
    socket.send("updateChannel," + deviceID + "," + newChannel)
}