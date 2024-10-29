//For theme settings under Appearance

const themes = ["","Dark","Light","Dark Blue"];
const accents = ["","Blue","Green","Orange","Red","Purple"];

const div_theme = document.getElementById("theme");
const div_accent = document.getElementById("accent");

const check_apply = document.getElementById("apply");

var apply = parseInt(sessionStorage.getItem("apply"));

if (apply === 1)
check_apply.checked = true;
else
check_apply.checked = false;

class toggle {

    constructor(num, mode)
    {
        this.num = num;
        this.mode = mode; //"theme" or "accent"

        this.button = document.createElement("button");
        if (sessionStorage.getItem(this.mode) === this.num.toString())
            this.button.classList.add("btn_active");
        else
            this.button.classList.add("btn_inactive");

        if (this.mode === "theme")
        {
            this.button.appendChild(document.createTextNode(themes[this.num]));
            div_theme.appendChild(this.button);
        }
        if (this.mode === "accent")
        {
            this.button.appendChild(document.createTextNode(accents[this.num]));
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
        sessionStorage.setItem(this.mode,this.num.toString());
        location.reload()
    }

}

let i = 1;
let button;
while (i < themes.length)
{
    new toggle(i,"theme");
    i += 1;
}

i = 1;
while (i < accents.length)
{
    new toggle(i,"accent");
    i += 1;
}

function switch_apply()
{
    apply = 1-apply;
    sessionStorage.setItem("apply" ,apply.toString())
    location.reload()
}

check_apply.addEventListener("click",switch_apply)
