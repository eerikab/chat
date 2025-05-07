//Applying themes on pages

const head = document.getElementsByTagName('head')[0];

//Get saved theming data
//localStorage seems to not work between file:// pages
let theme = parseInt(localStorage.getItem("theme")); 
let accent = parseInt(localStorage.getItem("accent"));
var apply = localStorage.getItem("apply");
var themes_data;


if (apply == null)
{
    apply = 1;
    localStorage.setItem("apply",apply.toString());
}
else
{
    apply = parseInt(apply);
}

if (!theme)
{
    theme = 0;
    localStorage.setItem("theme",theme.toString());
}
if (!accent)
{
    accent = 0;
    localStorage.setItem("accent",accent.toString());
}


let current_theme = themes_data["Themes"][theme];
let current_accent = themes_data["Accents"][accent];

css_theme = `html, body, button, input, textarea, .send,
    .topbar, .main, .userlist, .send_short,
    .postbtn, .adduser {
        background-color: ${current_theme["background"]};
        color: ${current_theme["text"]};
    }

    .comment {
        color: ${current_theme["comment"]};
    }

    aside, input, .account,
    .btn_inactive, textarea, .list_bottom {
        background-color: ${current_theme["sidebar"]};
    }

    .btn_inactive:hover, .postbtn:hover {
        background-color: ${current_theme["highlight"]};
    }

    .msg_background, .chatbox, .text_example, 
    .chatbox_short, .postbox, .userlist_box {
        background-color: ${current_theme["textbox"]};
    }

    .error {
        color: red;
    }`;

css_accent = `
    button, .btn_active {
        background-color: ${current_accent["button"]};
    }

    button:hover, .btn_active:hover {
        background-color: ${current_accent["button_highlight"]};
    }

    b {
        color: ${current_accent["selected_option"]};
    }

    a {
        color: ${current_accent["button"]};
    }

    a:hover {
        color: ${current_accent["button_highlight"]};
    }

    .user {
        color: ${current_accent["user"]};
    }`;

if (apply)
{
    var style = document.createElement("style");
    style.innerText = css_theme;
    head.appendChild(style);

    style = document.createElement("style");
    style.innerText = css_accent;
    head.appendChild(style);
}

/*//Insert theme
const link_theme = document.createElement('link');

link_theme.rel = "stylesheet";
link_theme.type = "text/css";
link_theme.href = "styles/themes/theme"+theme+".css";

head.appendChild(link_theme);

//Insert accent color
const link_accent = document.createElement('link');

link_accent.rel = "stylesheet";
link_accent.type = "text/css";
link_accent.href = "styles/accents/accent"+accent+".css";

head.appendChild(link_accent);*/
