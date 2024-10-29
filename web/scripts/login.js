//Scripting for Login and Register pages

//Clear user credentials from storage
sessionStorage.removeItem("username");
sessionStorage.removeItem("password");

function login()
{
    const entry_user = document.getElementById("name");
    const entry_password = document.getElementById("password");

    username = entry_user.value;
    password = entry_password.value;

    //Save values
    sessionStorage.setItem("username",username);
    sessionStorage.setItem("password",password);

    location.href = "posts.html"; //Go to next page
}

function register()
{
    const entry_user = document.getElementById("name");
    const entry_email = document.getElementById("email");
    const entry_password = document.getElementById("password");
    const entry_confirm = document.getElementById("confirm");

    username = entry_user.value;
    password = entry_password.value;
    
    //Check if passwords match
    if (password != entry_confirm.value)
    {
        entry_confirm.setCustomValidity("Passwords do not match");
        return;
    }
    else
    {
        entry_confirm.setCustomValidity("");
    }

    //Save values
    sessionStorage.setItem("username",username);
    sessionStorage.setItem("password",password);

    location.href = "posts.html"; //Go to next page
    
}

//Add function to submit buttons, if existing
const reg_form = document.getElementById("regform");
const log_form = document.getElementById("logform");

if (reg_form)
{
    reg_form.addEventListener("submit",(event) => {
        register();
        event.preventDefault();
    })
}

if (log_form)
{    
    log_form.addEventListener("submit",(event) => {
        login();
        event.preventDefault();
    })
}