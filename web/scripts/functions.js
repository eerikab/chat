//Functions shared between pages

var username;
var password;

//import {Server} from "socket.io";
//var net = require("net");
const url = "127.0.0.1";
const port = 9000;
const socket = new WebSocket("ws://localhost:9000");


function get_userdata()
{
    //Get user credentials
    username = sessionStorage.getItem("username");
    password = sessionStorage.getItem("password");
}

function request(text)
{
    console.log("request");

    //Request data from server
    /*var client = new net.Socket(); //Net socket
    client.connect(port, url, function() 
    {
        console.log('Connected');
        client.write(data);
    });

    client.on('data', function(data) {
        console.log('Received: ' + data);
        client.destroy(); // close client after server's response
    });*/

    //WebSocket
    socket.addEventListener("open", function() {
        socket.send(text);
    });
      
    // Listen for messages
    socket.addEventListener("message", (event) => {
        console.log("Message from server ", event.data);
    });

}

get_userdata();
request("version");