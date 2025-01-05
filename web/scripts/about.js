///Display versions on About page

const label_client = document.getElementById("ver_client");
const label_server = document.getElementById("ver_server");

label_client.textContent = "Client version " + version;
label_server.textContent = "Server version " + server_version;