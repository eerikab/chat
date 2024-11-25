///Functions for Account settings page

const id_label = document.getElementById("id_label");
const name_label = document.getElementById("name_label");
const btn_user = document.getElementById("btn_user");
const btn_pass = document.getElementById("btn_pass");
const btn_email = document.getElementById("btn_email");
const div_user = document.getElementById("div_user");
const div_pass = document.getElementById("div_pass");
const div_email = document.getElementById("div_email");
const div_save = document.getElementById("div_save");
const entry_user = document.getElementById("new_user");
const entry_email = document.getElementById("new_email");
const check_remember = document.getElementById("remember");

//if (!username)
//    location.href = "index.html";

div_user.style.display = "none";
div_pass.style.display = "none";
div_email.style.display = "none";
div_save.style.display = "none";

entry_user.value = username;

function display_user()
{
    id_label.textContent = "User ID: " + userid;
    name_label.textContent = "Username: " + username;
}

//Account data change
function show_settings_user()
{
    error_reset();
    div_user.style.display = "block";
    div_pass.style.display = "none";
    div_email.style.display = "none";
    div_save.style.display = "block";
}

function show_settings_pass()
{
    error_reset();
    div_user.style.display = "none";
    div_pass.style.display = "block";
    div_email.style.display = "none";
    div_save.style.display = "block";
}

function show_settings_email()
{
    error_reset();
    div_user.style.display = "none";
    div_pass.style.display = "none";
    div_email.style.display = "block";
    div_save.style.display = "block";
}

function submit_user()
{
    let change = entry_user.value;
    let passw = document.getElementById("current_user").value;
    
    hash_password(username,passw).then(function(passw_hash){
        if (change === "" || passw === "")
        {
            error_set("Please fill all fields");
            return;
        }
        if (change === username)
        {
            error_set("No changes made");
            return;
        }
        if (passw_hash !== pass_hash)
        {
            error_set("Invalid password");
            return;
        }
        
        if (change.length < 4 || change.length > 32)
        {
            error_set("Username must be 4-32 characters");
            return;
        }
        if (entry_user.validity.patternMismatch)
        {
            error_set("Username contains invalid characters");
            return;
        }

        hash_password(change,passw).then(function(pass_hash_new) {
            request_user("update","username\n"+change+"\n"+pass_hash_new,function() {
                username = change;
                pass_hash = pass_hash_new;
                display_user();
                remember_user();
                document.getElementById("current_user").value = "";
                
                error_set("Changes saved");
            })
        })
    })
}

function submit_pass()
{
    let change = document.getElementById("new_pass").value;
    let confirm = document.getElementById("confirm").value;
    let passw = document.getElementById("current_pass").value;
    
    hash_password(username,passw).then(function(passw_hash){
        if (change === "" || passw === "" || confirm === "")
        {
            error_set("Please fill all fields");
            return;
        }
        if (passw_hash !== pass_hash)
        {
            error_set("Invalid password");
            return;
        }

        if (change.length < 8 || change.length > 86)
        {
            error_set("Password must be 8-64 characters");
            return;
        }
        if (change !== confirm)
        {
            error_set("Passwords don't match");
            return;
        }
        hash_password(username,change).then(function(pass_hash_new) {
            if (pass_hash_new === pass_hash)
            {
                error_set("No changes made");
                return;
            }

            request_user("update","password\n"+pass_hash_new,function() {
                pass_hash = pass_hash_new;
                remember_user();
                document.getElementById("new_pass").value = "";
                document.getElementById("confirm").value = "";
                document.getElementById("current_pass").value = "";
                error_set("Changes saved");
            })
        })
    })
}

function submit_email()
{
    let change = entry_email.value;
    let passw = document.getElementById("current_email").value;
    
    hash_password(username,passw).then(function(passw_hash) {
        if (change === "" || passw === "")
        {
            error_set("Please fill all fields");
            return;
        }
        if (passw_hash !== pass_hash)
        {
            error_set("Invalid password");
            return;
        }

        if (entry_email.validity.typeMismatch)
        {
            error_set("Invalid email format");
            return;
        }

        hashing(change).then(function(email_hash_new) {
            request_user("update","email\n"+change+"\n"+email_hash_new,function() {
                entry_email.value = "";
                document.getElementById("current_email").value = "";
                error_set("Changes saved");
            })
        })
        
    })
}

function submit()
{
    if (div_user.style.display === "block")
        submit_user();
    else if (div_pass.style.display === "block")
        submit_pass();
    else if (div_email.style.display === "block")
        submit_email();

}

//Remember me check
if (localStorage.getItem("username"))
    check_remember.checked = true;

function remember_user()
{
    sessionStorage.setItem("username",username);
    sessionStorage.setItem("password",pass_hash);
    if (check_remember.checked)
    {
        localStorage.setItem("username",username);
        localStorage.setItem("password",pass_hash);
    }
    else
    {
        localStorage.removeItem("username");
        localStorage.removeItem("password");
    }
}
check_remember.addEventListener("click",remember_user);

error_reset();
display_user();