let username = "";
let userID = 0;
let password = "";
const reg_form = document.getElementById("regform");
//const log_form = document.getElementById("logform");

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

    const formdata = new FormData(reg_form);

    try
    {
        const response = fetch("posts.html", {
            method: "POST",
            body: formdata,
        })
        console.log(response.json());
    }
    catch(e)
    {
        console.error(e);
    }
    
}

reg_form.addEventListener("submit",(event) => {
    event.preventDefault();
    register();
})

/*log_form.addEventListener("submit",(event) => {
    event.preventDefault();
    register();
})*/