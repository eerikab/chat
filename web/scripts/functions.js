///Functions shared between pages

//Enable "release" to use production IP, otherwise use localhost
const release = 1;

//App version, increase with each released update
const version = "0.1.6";

//Declare variable
var username;
var password;
var pass_hash;
var userid;
var room;
var friend;
var sessionid;

let sidebar = 1;

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
const asides = document.getElementsByTagName("aside");

const div_main = document.querySelector(".main");
const chatbox_short = document.querySelector(".chatbox_short");
const chatbox = document.querySelector(".chatbox");
const postbox = document.querySelector(".postbox");
const userlist = document.querySelector(".contactlist");
const userbox = document.querySelector(".userlist_box");
const topbar = document.querySelector(".topbar");
const send = document.querySelector(".send");
const send_short = document.querySelector(".send_short");
const adduser = document.querySelector(".adduser");
const menu_toggle = document.querySelector(".menu_toggle");
const menu_toggle_long = document.querySelector(".menu_toggle_long");
const title_label = document.getElementById("page_title");

let months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];

function get_userdata()
{
    //Get user credentials from sessionstorage
    username = sessionStorage.getItem("username");
    userid = sessionStorage.getItem("userid");
    pass_hash = sessionStorage.getItem("password");
    sessionid = sessionStorage.getItem("sessionid");

    room = sessionStorage.getItem("room");
    friend = sessionStorage.getItem("friend");

    if (!room)
        room = "main";
    if (!friend)
        friend = "main";
}

function request_raw(text,func)
{
    error_reset();
    console.log("request",text);
    console.log(HOST + ":" + PORT);
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

            //If session ID has expired, log in again
            if (resp == "Error: Invalid session")
            {
                request_raw("login\n"+username+"\n"+pass_hash, update_user);
            }
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
    var msg = cmd+"\n"+userid+"\n"+pass_hash+"\n"+sessionid+"\n"+txt;
    request_raw(msg,func);
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
    if (sessionStorage.getItem("prevpage"))
    location.href = sessionStorage.getItem("prevpage");
    else
    location.href = "index.html";
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

function update_user(resp)
{
    //Update session ID and refresh
    sessionid = resp.split("\n")[1];
    sessionStorage.setItem("sessionid", sessionid);
    location.reload();
}

function toggle_sidebar()
{
    sidebar = !sidebar;
    for (let i = 0; i < asides.length; i++) {
        if (sidebar) 
        {
            asides[i].style.display = "block";
            
            //if (menu_toggle) menu_toggle.style.marginLeft = "16ch";
            //if (menu_toggle_long) menu_toggle_long.style.marginLeft = "20ch";
            if (div_main) div_main.style.marginLeft = "16ch";
            if (chatbox) chatbox.style.paddingLeft = "20ch";
            if (postbox) postbox.style.paddingLeft = "20ch";
            if (chatbox_short) chatbox_short.style.paddingLeft = "36ch";
            //if (userlist) userlist.style.marginLeft = "20ch";
            if (userbox) userbox.style.paddingLeft = "36ch";
            if (topbar) { 
                topbar.style.marginLeft = "20ch";
                topbar.style.paddingLeft = "2ch";
            }
            if (send) { 
                send.style.marginLeft = "20ch";
                send.style.width = "calc(100% - 20ch)";
            }
            if (send_short) { 
                send_short.style.marginLeft = "36ch";
                send_short.style.width = "calc(100% - 36ch)";
            }
            if (adduser) { 
                adduser.style.marginLeft = "36ch";
                adduser.style.width = "calc(100% - 36ch)";
            }
        }
        else 
        {
            asides[i].style.display = "none";

            if (menu_toggle) {
                menu_toggle.style.display = "block";
                menu_toggle.style.marginLeft = "0";
            }
            if (menu_toggle_long) {
                menu_toggle_long.style.display = "block";
                menu_toggle_long.style.marginLeft = "0";
            }
            if (div_main) div_main.style.marginLeft = "0";
            if (chatbox) chatbox.style.paddingLeft = "0";
            if (postbox) postbox.style.paddingLeft = "0";
            if (chatbox_short) chatbox_short.style.paddingLeft = "0";
            //if (userlist) userlist.style.marginLeft = "0";
            if (userbox) userbox.style.paddingLeft = "0";
            if (topbar) {
                topbar.style.marginLeft = "0";
                topbar.style.paddingLeft = "8ch";
            }
            if (send) { 
                send.style.marginLeft = "0";
                send.style.width = "100%";
            }
            if (send_short) { 
                send_short.style.marginLeft = "0";
                send_short.style.width = "100%";
            }
            if (adduser) { 
                adduser.style.marginLeft = "0";
                adduser.style.width = "100%";
            }
        }
    }
}

function check_width()
{
    if (innerWidth > 640) {
        if (!sidebar) toggle_sidebar();
    }
    else {
        if (sidebar) toggle_sidebar();
    }
}

window.addEventListener("resize", check_width);


get_userdata();
check_width();