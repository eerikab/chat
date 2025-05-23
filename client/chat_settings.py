'''Common tools functions that can be used by all windows\n
Set up data for themes and stufs\n'''

import os
import configparser
from hashlib import sha256
import re
import chat_global as cg
import datetime
import json
import asyncio
from websockets.legacy.client import connect
import webbrowser
import sys
import threading

def reset():
    #Reset all themes
    with open(cg.file_theme,"w") as settings:
        config = dict()

        config["Theme 1"] = {
            "name" : "Dark",
            "background" : "#333333",
            "textbox" : "#1e1e1e",
            "messagebox" : "#3f3f3f",
            "sidebar" : "#3f3f3f",
            "text" : "#f2f2f2",
            "highlight" : "#5a5a5a",
            "comment" : "#909090"
        }
        config["Theme 2"] = {
            "name" : "Light",
            "background" : "#f0f0f0",
            "textbox" : "#fcfcfc",
            "messagebox" : "#d8d8d8",
            "sidebar" : "#d8d8d8",
            "text" : "#202020",
            "highlight" : "#c0c0c0",
            "comment" : "#8c8c8c"
        }
        config["Theme 3"] = {
            "name" : "Dark Blue",
            "background" : "#000960",
            "textbox" : "#000920",
            "messagebox" : "#002078",
            "sidebar" : "#002078",
            "text" : "#f2f2f2",
            "highlight" : "#002eac",
            "comment" : "#909090"
        }
        config["Accent 1"] = {
            "name" : "Blue",
            "button" : "#008cff",
            "user" : "#00c8b7",
            "button_highlight" : "#00aaff",
            "selected_option" : "#00a0ff",
            "error" : "#ff0000"
        }
        config["Accent 2"] = {
            "name" : "Green",
            "button" : "#1caa00",
            "user" : "#00c01a",
            "button_highlight" : "#21c800",
            "selected_option" : "#1eb400",
            "error" : "#ff0000"
        }
        config["Accent 3"] = {
            "name" : "Orange",
            "button" : "#f07000",
            "user" : "#f06000",
            "button_highlight" : "#ff8000",
            "selected_option" : "#f07800",
            "error" : "#ff0000"
        }
        config["Accent 4"] = {
            "name" : "Red",
            "button" : "#f00028",
            "user" : "#f00054",
            "button_highlight" : "#ff2030",
            "selected_option" : "#f5002a",
            "error" : "#ff0000"
        }
        config["Accent 5"] = {
            "name" : "Purple",
            "button" : "#b400f0",
            "user" : "#ff00ff",
            "button_highlight" : "#c040ff",
            "selected_option" : "#bc00fa",
            "error" : "#ff0000"
        }
        config.write(settings)

def theming():
    sect = cg.theme
    themels = themes_data["Themes"][0]
    for i in themes_data["Themes"]:
        if i["name"] == sect:
            themels = i
    sect = cg.accent
    accentls = themes_data["Accents"]
    for i in themes_data["Accents"]:
        if i["name"] == sect:
            accentls = i
    return {**themels,**accentls} 

def default(args=""):
    #Dummy function, does nothing
    pass

async def send(command):
    #Communicate through websocket
    async with connect(f"{cg.HOST}:{cg.PORT}") as websocket:
        await websocket.send(command)
        return await websocket.recv()
    
async def broadcast(command=default):
    print("BROADCAST START start")
    async with connect(f"{cg.HOST}:{cg.PORT}") as websocket:
        print("BROADCAST START start")
        await websocket.send("broadcast" + "\n" + cg.userid + "\n" + cg.password + "\n" + cg.session)
        while True:
            message = await websocket.recv()
            print("\nBroadcast ",message)
            if "update" in message:
                command(message)

def run_broadcast(command=default):
    asyncio.run(broadcast(command))
    pass

def broadcast_start(command=default):
    target = threading.Thread(target=run_broadcast, daemon=True, args=(command,))
    target.start()
    #asyncio.create_task(broadcast(command))
    #asyncio.get_event_loop().run_forever()

def request(command):
    try:
        print("\nRequest",command)
        resp = asyncio.run(send(command))
        print("Response",resp)

        if resp[:5] == "Error" or resp[:12] == "Server error":
            update_user(resp)
            return False, resp
        
        return True, resp

    except Exception as e:
        resp = "Error: Could not connect to server"
        print(str(e))
        return False, resp

def hashing(name):
    return sha256(bytes(name,"utf-8")).hexdigest()

def hash_password(username,password):
    _pass_txt = "[user]"+username+"[pass]"+password
    _pass = sha256(bytes(_pass_txt,"utf-8")).hexdigest()
    return _pass

def regex_email(email):
    reg = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    if re.fullmatch(reg,email):
        return True
    else:
        return False
    
def regex_user(user):
    reg = r"[\w -_.]*"
    if re.fullmatch(reg,user):
        return True
    else:
        return False
    
def load_line(line, default=""):
    #Set variable value from save file via line number
    #Set to default when empty
    try:
        with open(cg.file_settings,"r") as file:
            lines = file.readlines()

            var = lines[line].strip()
            if var == "":
                var = default
    except:
        var = default

    return var
    
def load_user():
    cg.user = load_line(0)
    cg.password = load_line(1)
    cg.theme = load_line(2, "Dark")
    cg.accent = load_line(3, "Blue")
    cg.apply_theme = int(load_line(4, 1))

def save_user():
    with open(cg.file_settings,"w") as file:
        if cg.remember:
            file.write(cg.user)
            file.write("\n"+cg.password)
        else:
            file.write("\n")
        file.write("\n"+cg.theme)
        file.write("\n"+cg.accent)
        file.write("\n"+str(cg.apply_theme))

def time_format(time_str=""):
    #2024-03-26 18:43 -> 26 Mar 2024 18:43
    if time_str == "":
        time_str = str(datetime.datetime.now(datetime.timezone.utc))

    dt_utc = datetime.datetime.fromisoformat(time_str[:16]+":00+00:00")
    dt_local = str(dt_utc.astimezone())
    
    year = dt_local[:4]
    month = dt_local[5:7]
    day = dt_local[8:10]
    hour = dt_local[11:13]
    minute = dt_local[14:16]

    try:
        return day+" "+cg.months[int(month)]+" "+year+" "+hour+":"+minute
    except:
        return day+"/"+month+"/"+year+" "+hour+":"+minute

def json_decode(string):
    return json.loads(string)

def url(page):
    webbrowser.open(page)

def version():
    return sys.version.split()[0]

def update_user(resp):
    #If session has expired, request a new one
    if resp == "Error: Invalid session":
        ch, resp = request("login\n"+cg.user+"\n"+cg.password)
        if ch:
            cg.session = resp.split("\n")[1]

    

#Init

#Create config directory
os.makedirs(cg.directory+"/config", exist_ok=True) 

#Create settings file if not available
try:
    with open(cg.file_theme,"r") as file:
        #If the file is empty, set themes
        if not file.read():
            reset()
except:
    reset()

#reset()

#Load theming config
with open(cg.file_theme) as file:
    config = file.read()
    themes_data = json.loads(config)

load_user()

themed = 0
broadcast_function = default