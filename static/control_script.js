var messageBoard = document.getElementById('messageBoard');

socket.addEventListener('message', ev => {
        const devices = JSON.parse(ev.data);        
        for (const device of devices){
            $('#' + device['id']).attr('class', device['cssActivationClass']);
        }  
});

function toggle(deviceID) {
    socket.send("toggle," + deviceID);
}