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

