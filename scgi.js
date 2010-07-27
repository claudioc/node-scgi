
var sys = require("sys"),
    urlparser = require('url'),
    net = require("net"),
    stream;

var Client = new process.EventEmitter();

exports.getClient = function() {
  return Client;
}

Client.request = function(resource, headers, handler) {

  stream = new net.Stream();
  stream.setEncoding("UTF8");
  stream.connect(4000, '127.0.0.1');

  stream.on("connect", function() {
      
    Client.emit('connect');
    
    var resParsed = urlparser.parse(resource);
    
    var h = [ 
      "CONTENT_LENGTH"  + String.fromCharCode(0) + "0" + String.fromCharCode(0),
      "SCGI"            + String.fromCharCode(0) + "1" + String.fromCharCode(0),
      "HTTP_USER_AGENT" + String.fromCharCode(0) + headers['user-agent'] + String.fromCharCode(0),
      "HTTP_ACCEPT"     + String.fromCharCode(0) + headers['accept'] + String.fromCharCode(0),
      "HTTP_HOST"       + String.fromCharCode(0) + headers['host'] + String.fromCharCode(0),
      "HTTP_CONNECTION" + String.fromCharCode(0) + headers['connection'] + String.fromCharCode(0),
      "REQUEST_METHOD"  + String.fromCharCode(0) + "GET" + String.fromCharCode(0),
      "REQUEST_URI"     + String.fromCharCode(0) + resParsed.href + String.fromCharCode(0),
      "SCRIPT_NAME"     + String.fromCharCode(0) + resParsed.pathname + String.fromCharCode(0),
      "QUERY_STRING"    + String.fromCharCode(0) + (resParsed.query || '') + String.fromCharCode(0),
    ];
    
    var tl=0;
    for (var i=0; i < h.length; i++) {
      tl += h[i].length;
    }
    var message = tl + ":" + h.join("") + ",";
    stream.write(message);
  });
  
  stream.on("end", function() {
    //console.log("Disconnected");
  });
  
  stream.on('data', function(data) {
      
    // FIXME handle the case of a \r\n\r\n pair in the body
      
    // Split headers and body
    var h_b = data.split("\r\n\r\n");
    // Split headers
    var h = h_b[0].split("\r\n");
    /* First header is status */
    var headers = {}, pair;
    for (var i = 1; i < h.length; i++) {
      pair = h[i].split(": ");
      headers[pair[0]] = pair[1];
    }
      
    stream.end();
    
    handler(parseInt(h[0].replace("Status: ", "")), headers, h_b[1]);
  });
  
}

