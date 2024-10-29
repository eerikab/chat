//Applying themes on pages

const head = document.getElementsByTagName('head')[0];

//Get saved theming data
//localStorage seems to not work between file:// pages
let theme = parseInt(sessionStorage.getItem("theme")); 
let accent = parseInt(sessionStorage.getItem("accent"));
var apply = sessionStorage.getItem("apply");

if (apply == null)
{
    apply = 1;
    sessionStorage.setItem("apply",apply.toString());
}
else
{
    apply = parseInt(apply);
}

if (!theme)
{
    theme = 1;
    sessionStorage.setItem("theme",theme.toString());
}
if (!accent)
{
    accent = 1;
    sessionStorage.setItem("accent",accent.toString());
}

if (apply)
{
    //Insert theme
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

    head.appendChild(link_accent);
}