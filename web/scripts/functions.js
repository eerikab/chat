///Functions shared between pages

//Declare variable
var username;
var password;
var pass_hash;
var userid;

//import {Server} from "socket.io";
//var net = require("net");
const url = "127.0.0.1";
const port = 9000;

var server_version = sessionStorage.getItem("version");

const error = document.querySelector(".error");

function get_userdata()
{
    //Get user credentials
    username = sessionStorage.getItem("username");
    userid = sessionStorage.getItem("userid");
    pass_hash = sessionStorage.getItem("password");
}

function request_raw(text,func)
{
    error_reset()
    console.log("request",text);
    const socket = new WebSocket("ws://localhost:9000");

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

    socket.addEventListener("error",function() {
        error.textContent = "Could not connect to server";
    })
      
    // Listen for messages
    socket.addEventListener("message", (event) => {
        var resp = event.data.toString();
        console.log("Message from server ", resp);

        //If the command is successful, execute function, otherwise write out the error
        if (resp.substring(0,5) === "Error" || resp.substring(0,12) === "Server error")
        {
            error.textContent = resp;
        }
        else 
        {
            func(resp);
        }
    });
}

async function hashing(text)
{
    //Why is hashing so complicated here?
    const enc = new TextEncoder().encode(text); // encode as (utf-8) Uint8Array
    const hash = await window.crypto.subtle.digest("SHA-256", enc); // hash the message
    const hashArray = Array.from(new Uint8Array(hash)); // convert buffer to byte array
    const hex = hashArray
        .map((b) => b.toString(16).padStart(2, "0"))
        .join(""); // convert bytes to hex string
    return hex;

    /*Using the command:
    hashing(text).then((hash) => {
        hash;
    });
    */
}

async function hash_password(username,password)
{
    pass_txt = "[user]"+username+"[pass]"+password;
    pass_hash = await hashing(pass_txt);
}

function request_user(cmd,txt,func)
{
    //Server request after user has logged in, includes authentication
    var msg = cmd+"\n"+userid+"\n"+pass_hash+"\n"+txt;
    request_raw(msg,func)
}

function error_set(txt)
{
    console.log(txt);
    error.textContent = txt;
}

function error_reset()
{
    error.textContent = "";
}

get_userdata();