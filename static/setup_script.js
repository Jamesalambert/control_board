$(document).ready(displayChannelSettings);

socket.addEventListener('message', ev => {
        const devices = JSON.parse(ev.data);
        
        for (const device of devices){
            $(`[id^=${device['id']}]`).each(function(i, button){
                $(button).attr('id', `${device['id']}-${device['channel']}`);
            });
        }
        
        displayChannelSettings();
        
        // $('.setChannelButtons > button').attr('class', 'off');
//                     
//         for (const device of devices){
//             $('#' + device['id'] + '-' + device['channel'] + '-' + device['channel']).attr('class', 'on');
//         }
});

function displayChannelSettings(){
    $('.setChannelButtons > button').each( function(index, button){
        const channel = $(button).attr('id').split("-")[1];
        const targetClass = $(button).attr('class').split(" ")[0];
        console.log(`${channel} ${targetClass}`);
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