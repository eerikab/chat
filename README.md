A simple messaging platform, featuring posts and direct messages

Made for desktop and web with Python and basic HTML

Working title TickChat

Access web edition at https://eerikab.github.io/chat/

## Setup
Python 3 is required with Tkinter, Websockets, Psycopg2 modules

Tkinter is in Python standard library, but not included by default on Linux. To install all necessary Python modules on Debian/Ubuntu, use
```
sudo apt install python3-tk python3-websockets python3-psycopg2
```
Otherwise install websockets through pip
```
pip install websockets psycopg2
```

## Usage
To run desktop client, execute `run_chat.sh` or
```
python3 client/chat_main.py
```

To run the website locally, run `serve_web.sh`
<br>You can then access it on http://localhost:8000

To host the server locally, run
```
python3 server/chat_server.py
```
