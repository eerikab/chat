//Functions shared between pages

var username;
var password;

let url = "ws://127.0.0.1:9999";

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
    socket = new WebSocket(url);

    //Send message on successful connection
    socket.onopen = (event) =>
    {
        socket.send(text);
    }
    
    //Receive response
    socket.onmessage = (event) =>
    {
        alert(event.data);
        socket.close()
    }
}

get_userdata();
request();