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
from websockets.client import connect
import webbrowser
import sys

def reset():
    #Reset all themes
    with open(cg.file_theme,"w") as settings:
        config = configparser.ConfigParser()

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
    config = configparser.ConfigParser()
    config.read(cg.file_theme)
    sect = cg.theme
    themels = themelist[0]
    for i in themelist:
        if i["name"] == sect:
            themels = i
    sect = cg.accent
    accentls = accentlist[0]
    for i in accentlist:
        if i["name"] == sect:
            accentls = i
    return {**themels,**accentls} 

async def send(command):
    #Communicate through websocket
    async with connect(f"{cg.HOST}:{cg.PORT}") as websocket:
        await websocket.send(command)
        return await websocket.recv()

def request(command):
    try:
        print("\nRequest",command)
        resp = asyncio.run(send(command))
        print("Response",resp)

        if resp[:5] == "Error" or resp[:12] == "Server error":
            return False, resp
        
        return True, resp

    except Exception as e:
        resp = "Error: " + str(e)
        print(resp)
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
    
def load_line(lines, line, default=""):
    try:
        var = lines[line].strip()
    except:
        var = default

    return var
    
def load_user():
    with open(cg.file_settings,"r") as file:
        lines = file.readlines()
        
        cg.user = load_line(lines, 0)
        cg.password = load_line(lines, 1)
        cg.theme = load_line(lines, 2)
        cg.accent = load_line(lines, 3)
        cg.apply_theme = int(load_line(lines, 4, 1))

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
    
def ini_to_json():
    #Converts theming configuration from INI to JSON
    config = configparser.ConfigParser()
    config.read(cg.directory+"/config/chat_themes.ini")
    config_dict = dict()
    for i in config.sections():
        config_dict[i] = dict(config.items(i))
    print(config_dict)
    config_json = json.dumps(config_dict,indent=4)
    with open(cg.directory+"/config/chat_themes.json","w") as file:
        file.write(config_json)

def json_decode(string):
    return json.loads(string)

def url(page):
    webbrowser.open(page)

def version():
    return sys.version.split()[0]
    

#Init

#Create settings file if not available
try:
    with open(cg.file_theme,"r"):
        pass
except:
    reset()

#reset()

#Open config file for reading
config = configparser.ConfigParser()
config.read(cg.file_theme)

#Get theme settings
themelist = []
i = 1
while True:
    sect = "Theme "+str(i)
    if config.has_section(sect):
        theme_values = {
            "name" : config.get(sect,"name"),
            "bg" : config.get(sect,"background"),
            "textbox" : config.get(sect,"textbox"),
            "msg" : config.get(sect,"messagebox"),
            "side" : config.get(sect,"sidebar"),
            "text" : config.get(sect,"text"),
            "high" : config.get(sect,"highlight"),
            "comment" : config.get(sect,"comment")
        }
        themelist.append(theme_values)
        i+=1
    else:
        break

accentlist = []
i = 1
while True:
    sect = "Accent "+str(i)
    if config.has_section(sect):
        accent = {
            "name" : config.get(sect,"name"),
            "button" : config.get(sect,"button"),
            "user" : config.get(sect,"user"),
            "button_high" : config.get(sect,"button_highlight"),
            "selected" : config.get(sect,"selected_option"),
            "error" : config.get(sect,"error"),
        }
        accentlist.append(accent)
        i+=1
    else:
        break

theme_names = []
for i in themelist:
        theme_names.append(i["name"])

accent_names = []
for i in accentlist:
        accent_names.append(i["name"])

load_user()

themed = 0