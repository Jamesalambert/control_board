$(document).ready(displayChannelSettings);


socket.addEventListener('message', ev => {
        const devices = JSON.parse(ev.data);
        
//         highlight correct channels without waiting for a page reload
        for (const device of devices){
            const deviceID = device['id'];
            const channel = device['channel'];
            $(`[id^=${deviceID}-]`).each(function(i, button){
                $(button).attr('id', `${deviceID}-${channel}`);
            });
        }
        displayChannelSettings();
});

function displayChannelSettings(){
    $('.setChannelButtons > button').each( function(index, button){
        const channel = $(button).attr('id').split("-")[1];
        const targetClass = $(button).attr('class').split(" ")[0];
        if (channel == targetClass){
            $(button).addClass('on');
            $(button).removeClass('off');
        } else {
            $(button).addClass('off');
            $(button).removeClass('on');
        }
    });
}


function updateChannel(deviceID, newChannel){
    socket.send("updateChannel," + deviceID + "," + newChannel);
}