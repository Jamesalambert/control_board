var socket = new WebSocket('ws://' + location.host + '/sock');
setInterval(checkConnection, 2 * 1000);
$(document).ready(updateMenu);



socket.addEventListener('message', ev => {
//         check for updates regarding the serial connection
    const messageData = JSON.parse(ev.data);
    if (typeof(messageData) == "string"){
        const messageParts = messageData.split(",")
        const messageType = messageParts[0];
        const message = messageParts[1];
        if (messageType == "isConnected"){
            if (message == "True"){
                $('#messageBoard').addClass('connected');
                $('#messageBoard').html("serial connection: [   ok  ]")
            } else {
                $('#messageBoard').removeClass('connected');
                $('#messageBoard').html("serial connection: [   fail  ]")
            }
        }
    }
});

function checkConnection(){
    socket.send('x');
}

function updateMenu(){
    $(`#${document.title.split(' ')[0].toLowerCase()}-nav`).toggleClass('active');
}
