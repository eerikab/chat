//For theme settings under Appearance

const div_theme = document.getElementById("theme");
const div_accent = document.getElementById("accent");
const check_apply = document.getElementById("apply");
const account_button = document.getElementById("btn_account");
const date_comment = document.getElementById("test_time");

if (!username)
    account_button.remove();

var apply = parseInt(localStorage.getItem("apply"));

if (apply === 1)
check_apply.checked = true;
else
check_apply.checked = false;

date_comment.textContent = time_format(Date(), false);

class toggle {
    constructor(num, mode)
    {
        this.num = num;
        this.mode = mode; //"theme" or "accent"

        this.button = document.createElement("button");
        if (localStorage.getItem(this.mode) === this.num.toString())
            this.button.classList.add("btn_active");
        else
            this.button.classList.add("btn_inactive");

        if (this.mode === "theme")
        {
            this.button.appendChild(document.createTextNode(themes_data["Themes"][num]["name"]));
            div_theme.appendChild(this.button);
        }
        if (this.mode === "accent")
        {
            this.button.appendChild(document.createTextNode(themes_data["Accents"][num]["name"]));
            div_accent.appendChild(this.button);
        }
        this.button.addEventListener("click",(event) => {
            this.onclick();
            event.preventDefault(); //Prevent default refresh to not clear button variables
        });
    }

    onclick()
    {
        console.log(this.num,this.mode);
        localStorage.setItem(this.mode,this.num.toString());
        location.reload()
    }

}

function create_theme_toggles()
{
    var i = 0;
    let button;
    while (i < themes_data["Themes"].length)
    {
        new toggle(i,"theme");
        i += 1;
    }

    i = 0;
    while (i < themes_data["Accents"].length)
    {
        new toggle(i,"accent");
        i += 1;
    }
}

function switch_apply()
{
    apply = 1-apply;
    localStorage.setItem("apply" ,apply.toString())
    location.reload()
}

check_apply.addEventListener("click",switch_apply)
create_theme_toggles();