A simple messaging platform, featuring posts and direct messages

Made in Python and basic HTML

Working title TickChat

## Setup
Python 3 is required with Tkinter and Websockets modules

Tkinter is in Python standard library, but not included on Linux. To install necessary modules on Debian/Ubuntu, use
```
sudo apt install python3-tk python3-websockets
```
Otherwise install websockets through pip
```
pip install websockets
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
