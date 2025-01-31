///Display versions on About page

const label_client = document.getElementById("ver_client");
const label_server = document.getElementById("ver_server");
const account_button = document.getElementById("btn_account");

if (!username)
    account_button.remove();

label_client.textContent = "Client version " + version;
if (server_version)
    label_server.textContent = "Server version " + server_version;
else
    label_server.remove();