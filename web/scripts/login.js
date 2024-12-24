///Scripting for Login and Register pages

//Clear user credentials from storage
sessionStorage.removeItem("username");
sessionStorage.removeItem("userid");
sessionStorage.removeItem("password");
sessionStorage.removeItem("room");
sessionStorage.removeItem("friend");

username = "";
password = "";
pass_hash = "";
userid = "";
var email = "";

sessionStorage.setItem("prevpage",location.href);

const entry_user = document.getElementById("name");
const entry_email = document.getElementById("email");
const entry_password = document.getElementById("password");
const entry_confirm = document.getElementById("confirm");
const check_remember = document.getElementById("remember");

function load_data()
{
    //Log in automatically if user is saved
    let local_name = localStorage.getItem("username");
    let local_pass = localStorage.getItem("password");
    console.log(local_name,local_pass);
    if (local_name && local_pass)
    {
        username = local_name;
        pass_hash = local_pass;
        request_raw("login\n"+username+"\n"+pass_hash,login);
    }
}

function login(resp)
{
    //Save values
    userid = resp;
    sessionStorage.setItem("username",username);
    sessionStorage.setItem("userid",userid);
    sessionStorage.setItem("password",pass_hash);

    if (check_remember && check_remember.checked)
    {
        localStorage.setItem("username",username);
        localStorage.setItem("password",pass_hash);
    }

    location.href = "posts.html"; //Go to next page
}

function submit_login()
{
    username = entry_user.value;
    password = entry_password.value;
    error_reset();

    //Error checking
    if (username === "" || password === "")
    {
        error_set("Please fill all fields");
        return;
    }

    //Hash password and submit data
    hash_password(username,password).then(function(hash){
        pass_hash = hash;
        request_raw("login\n"+username+"\n"+pass_hash,login);
    })
}

function submit_register()
{
    username = entry_user.value;
    email = entry_email.value;
    password = entry_password.value;
    confirm_value = entry_confirm.value;
    error_reset();

    //Error checking
    //Custom messages are used over Validity, because the messages can be slightly hard to find
    if (username === "" || password === "" || email === "" || confirm_value === "")
    {
        error_set("Please fill all fields");
        return;
    }
    if (username.length < 4 || username.length > 32)
    {
        error_set("Username must be 4-32 characters");
        return;
    }
    if (password.length < 8 || password.length > 64)
    {
        error_set("Username must be 8-64 characters");
        return;
    }
    if (password !== confirm_value)
    {
        error_set("Passwords do not match");
        return;
    }
    if (entry_email.validity.typeMismatch)
    {
        error_set("Invalid email format");
        return;
    }
    if (entry_user.validity.patternMismatch)
    {
        error_set("Username contains invalid characters");
        return;
    }

    //Hash sensitive data and submit user
    hash_password(username,password).then(function(hash){
        pass_hash = hash;
        hashing(email).then(function(email_hash){
        request_raw("register\n"+username+"\n"+pass_hash+"\n"+email_hash,login);
    })});
}

//Get server version
function get_version(resp)
{
    server_version = resp;
    sessionStorage.setItem("version",resp);
    load_data();
}

if (!server_version)
    request_raw("version",get_version);