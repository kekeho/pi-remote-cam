// Copyright (c) 2019 Hiroki Takemura (kekeho)
// 
// This software is released under the MIT License.
// https://opensource.org/licenses/MIT

namespace = '/socket'
let socket = io.connect('http://' + document.domain + ':' + location.port + namespace);

let shot_button = document.getElementById('shot');
shot_button.onclick = function() {
    socket.emit('shot', {});
};

let interval_shot_button = document.getElementById('interval-shot');
let interval_sec_param = document.getElementById('interval-sec');
interval_shot_button.onclick = function() {
    if (interval_shot_button.attributes['shooting'].nodeValue === 'false'){
        socket.emit('interval-shot', {'sec': interval_sec_param.value});
        interval_shot_button.innerText = 'Stop';
        interval_shot_button.setAttribute('shooting', 'true');
    } else {
        socket.emit('stop-interval', {});
        interval_shot_button.innerText = 'Interval';
        interval_shot_button.setAttribute('shooting', 'false');
    }
};

function create_image_col(img_path) {
    let col = document.createElement('div');
    col.classList = ['col-3'];
    
    let image = document.createElement('img');
    image.setAttribute('src', img_path);

    col.appendChild(image)

    let images_row = document.getElementById('taken-images');
    images_row.appendChild(col);
}

socket.on('new-images', function(message) {
    for (const index in message) {
        create_image_col(message[index]);
    }
});

window.onload = function() {
    socket.emit('get-all-taken-images', {});
}

