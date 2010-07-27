
var sys       = require('sys'),
    scgi      = require("./scgi"),
    urlparser = require('url'),
    http      = require('http');

var nc = 0;

var scgiClient = scgi.getClient();

scgiClient.on('connect', function(data) {
//  console.log("Client " + nc + " connected :)");
  nc++;
});

var server = http.createServer(function (request, response) {
  if (urlparser.parse(request.url).pathname.match(/\/scgi\/(.*)$/)) {
    scgiClient.request(request.url.replace('scgi/',''), request.headers, function(status, headers, body) {
      response.writeHead(status, headers);
      response.write(body);
      response.end();
    });
  } else {
    response.writeHead(200, {"Content-Type": "text/plain"});
    response.write("Hello World\n");
    response.end();
  }
});

// Listen on port 8000, IP defaults to 127.0.0.1
server.listen(8000);

// Put a friendly message on the terminal
sys.puts("Server running at http://127.0.0.1:8000/");

