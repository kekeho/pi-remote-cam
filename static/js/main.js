// Copyright (c) 2019 Hiroki Takemura (kekeho)
// 
// This software is released under the MIT License.
// https://opensource.org/licenses/MIT

namespace = '/socket';
let socket = io.connect('http://' + document.domain + ':' + location.port + namespace);


// When click shot button, send signal to server
let shot_button = document.getElementById('shot');
shot_button.onclick = function() {
    socket.emit('shot', {});
};


// When click record button, send signal to server
let record_button = document.getElementById('record');
record_button.onclick = function() {
    if (record_button.innerText === 'Record'){
        // start recording
        socket.emit('start_recording');
        record_button.innerText = 'Stop Record';
    } else {
        // stop recording
        socket.emit('stop_recording');
        record_button.innerText = 'Record';
    }
}


// When click set-time button, get current date from client, send to raspberry pi
let set_time_button = document.getElementById('set-time');
set_time_button.onclick = function() {
    let d = new Date();  // current time
    socket.emit('set-date', d.toUTCString()); 
}

socket.on('set-date-result', function(message) {
    let indicator = document.getElementById('set-time-indicator');
    if (message === 0) {
        indicator.innerText = 'updated';
    } else {
        indicator.innerText = 'ERROR HAS OCCURRED';
    }
});


// When click shutter speed button, send to raspberry pi
let set_shutter_button = document.getElementById('set-shutterspeed');
set_shutter_button.onclick = function() {
    let microsec_form = document.getElementById('shutterspeed-form');

    let microsec = null;
    if (parseInt(microsec_form.value) === 0) {
        microsec = 0;  // auto
    } else {
        microsec = parseInt(1 / parseInt(microsec_form.value) * 1e6);
    }

    socket.emit('set-shutterspeed', microsec);
};


// When click interval-shot button, send signal(set interval or clear) to server
let interval_shot_button = document.getElementById('interval-shot');
let interval_sec_param = document.getElementById('interval-sec');
interval_shot_button.onclick = function() {
    if (interval_shot_button.attributes['shooting'].nodeValue === 'false'){
        // Clear interval
        socket.emit('interval-shot', {'sec': interval_sec_param.value});
        interval_shot_button.innerText = 'Stop';
        interval_shot_button.setAttribute('shooting', 'true');
    } else {
        // Set interval
        socket.emit('stop-interval', {});
        interval_shot_button.innerText = 'Interval';
        interval_shot_button.setAttribute('shooting', 'false');
    }
};


// Insert taken images to garally
function create_image_col(img_path) {
    let col = document.createElement('div');
    col.classList = ['col-3'];
    
    let image = document.createElement('img');
    image.setAttribute('src', img_path);

    col.appendChild(image)

    let images_row = document.getElementById('taken-images');
    images_row.appendChild(col);
}
// When receive new-images signal, insert images to garally
socket.on('new-images', function(message) {
    for (const index in message) {
        create_image_col(message[index]);
    }
});


// Sync to sever
window.onload = function() {
    socket.emit('get-all-taken-images', {});
}
