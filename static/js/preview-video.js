// Copyright (c) 2019 Hiroki Takemura (kekeho)
// 
// This software is released under the MIT License.
// https://opensource.org/licenses/MIT

namespace = '/preview-stream'
let socket = io.connect('http://' + document.domain + ':' + location.port + namespace);

socket.on('video-frame', function(message) {
    console.log(message.frame)
})
