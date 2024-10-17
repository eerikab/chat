//Functions shared between pages

var username;
var password;

function get_userdata()
{
    username = sessionStorage.getItem("username");
    password = sessionStorage.getItem("password");
}


get_userdata()