///Functions shared between pages

//Enable "release" to use production IP, otherwise use localhost
const release = 0

//App version, increase with each released update
const version = "0.1.0a3"

//Declare variable
var username;
var password;
var pass_hash;
var userid;
var room;
var friend;

//Networking
let HOST = "ws://localhost"; //Local address for testing
let PORT = "9000";

if (release)
{
    HOST = "wss://chat-4zh4.onrender.com"; //Public address of server
    PORT = "";
}

let server_version = sessionStorage.getItem("version");

let error = document.querySelector(".error");

let months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

function get_userdata()
{
    //Get user credentials from sessionstorage
    username = sessionStorage.getItem("username");
    userid = sessionStorage.getItem("userid");
    pass_hash = sessionStorage.getItem("password");

    room = sessionStorage.getItem("room");
    friend = sessionStorage.getItem("friend");

    if (!room)
        room = "main";
    if (!friend)
        friend = "main";
}

function request_raw(text,func)
{
    error_reset()
    console.log("request",text);
    console.log(HOST + ":" + PORT)
    const socket = new WebSocket(HOST + ":" + PORT);

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
    let pass_txt = "[user]"+username+"[pass]"+password;
    return await hashing(pass_txt);
}

function request_user(cmd="",txt="",func=dummy)
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

function go_back()
{
    location.href = sessionStorage.getItem("prevpage");
}

function time_format(time, utc=true)
{
    if (utc)
        time += " UTC"
    let date = new Date(time);
    let date_str = date.getDate() + " " + months[date.getMonth()] + " " + date.getFullYear() + " " + date.getHours().toString().padStart(2,"0") + ":" + date.getMinutes().toString().padStart(2,"0");
    return date_str;
}

function add_text(node, text)
{  
    var txt_node = document.createTextNode(text);
    node.appendChild(txt_node);
}

function add_node(node, text, html_class="span", add_class="comment")
{
    var txt = document.createElement(html_class);
    var txt_node = document.createTextNode(text);
    txt.appendChild(txt_node);
    if (add_class)
        txt.classList.add(add_class);
    node.appendChild(txt);
}

function id_to_room(other_id)
{
    if (parseInt(userid) < parseInt(other_id))
        return "room" + userid + other_id;
    else
        return "room" + other_id + userid;
}

function dummy()
{
    return;
}

get_userdata();