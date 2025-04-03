A simple messaging platform, featuring posts and direct messages

Made for desktop and web with Python and basic HTML, CSS, JavaScript

Working title TickChat

Access web edition at https://eerikab.github.io/chat/

To simply use the desktop application, download the latest package from [Releases](https://github.com/eerikab/chat/releases)

## Setup
Uses Python 3. Tkinter, Websockets, Psycopg2 modules are needed for desktop and server and Pyinstaller for exporting

Tkinter is in Python standard library, but not included by default on Linux. To install all necessary Python modules for running the application on Debian/Ubuntu, use
```
sudo apt install python3-tk python3-websockets python3-psycopg2
```
Otherwise install additional modules through pip
```
pip install -r requirements.txt
```

For the best experience on desktop, install Montserrat font

## Usage
To run desktop client, execute `run_chat.sh` or
```
python3 client/chat_main.py
```

To run the website locally, run `serve_web.sh` in `scripts`
<br>You can then access it on http://localhost:8000

To host the server locally, run
```
python3 server/chat_server.py
```
