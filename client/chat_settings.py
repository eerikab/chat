import os
import configparser
from hashlib import sha256
import re
import socket

'''Common tools functions that can be used by all windows
Set up data for themes and stufs'''

class settings():
    def __init__(self) -> None:
        self.file_theme = os.path.dirname(__file__)+"/chat_themes.ini"
        self.file_settings = os.path.dirname(__file__)+"/chat_settings.txt"
        #self.font = os.path.dirname(__file__)+"/fonts/Cantarell.ttf"
        #self.font_bold = os.path.dirname(__file__)+"/fonts/Cantarell-Bold.ttf"

        #Create settings file if not available
        try:
            with open(self.file_theme,"r"):
                pass
        except:
            self.reset()

        self.reset()

        #Open config file for reading
        config = configparser.ConfigParser()
        config.read(self.file_theme)

        #Get theme settings
        self.themelist = []
        i = 1
        while True:
            sect = "Theme "+str(i)
            if config.has_section(sect):
                theme = {
                    "name" : config.get(sect,"Name"),
                    "bg" : config.get(sect,"Background"),
                    "textbox" : config.get(sect,"Textbox"),
                    "msg" : config.get(sect,"Messagebox"),
                    "side" : config.get(sect,"Sidebar"),
                    "text" : config.get(sect,"Text"),
                    "high" : config.get(sect,"Highlight"),
                    "comment" : config.get(sect,"Comment")
                }
                self.themelist.append(theme)
                i+=1
            else:
                break

        self.accentlist = []
        i = 1
        while True:
            sect = "Accent "+str(i)
            if config.has_section(sect):
                accent = {
                    "name" : config.get(sect,"Name"),
                    "button" : config.get(sect,"Button"),
                    "user" : config.get(sect,"User"),
                    "button_high" : config.get(sect,"Button highlight"),
                    "selected" : config.get(sect,"Selected option"),
                }
                self.accentlist.append(accent)
                i+=1
            else:
                break

        self.theme_names = []
        for i in self.themelist:
                self.theme_names.append(i["name"])

        self.accent_names = []
        for i in self.accentlist:
                self.accent_names.append(i["name"])

        self.themed = 0

    def reset(self):
        #Reset all themes
        with open(self.file_theme,"w") as settings:
            config = configparser.ConfigParser()
            '''config["Themes"] = {
                "Theme 1" : "Dark",
                "Theme 2" : "Light",
                "Accent 1" : "Blue",
                "Accent 2" : "Green",
                "Accent 3" : "Orange",
                "Accent 4" : "Red",
                "Accent 5" : "Purple"
            }'''

            config["Theme 1"] = {
                "Name" : "Dark",
                "Background" : "#333333",
                "Textbox" : "#1e1e1e",
                "Messagebox" : "#3f3f3f",
                "Sidebar" : "#3f3f3f",
                "Text" : "#f2f2f2",
                "Highlight" : "#5a5a5a",
                "Comment" : "#909090"
            }
            config["Theme 2"] = {
                "Name" : "Light",
                "Background" : "#ececec",
                "Textbox" : "#fafafa",
                "Messagebox" : "#dcdcdc",
                "Sidebar" : "#dcdcdc",
                "Text" : "#202020",
                "Highlight" : "#c8c8c8",
                "Comment" : "#8c8c8c"
            }
            config["Accent 1"] = {
                "Name" : "Blue",
                "Button" : "#008cff",
                "User" : "#00c8b7",
                "Button highlight" : "#00aaff",
                "Selected option" : "#00a0ff",
            }
            config["Accent 2"] = {
                "Name" : "Green",
                "Button" : "#1caa00",
                "User" : "#00c01a",
                "Button highlight" : "#21c800",
                "Selected option" : "#1eb400",
            }
            config["Accent 3"] = {
                "Name" : "Orange",
                "Button" : "#f07000",
                "User" : "#f06000",
                "Button highlight" : "#ff8000",
                "Selected option" : "#f07800",
            }
            config["Accent 4"] = {
                "Name" : "Red",
                "Button" : "#f00028",
                "User" : "#f00054",
                "Button highlight" : "#ff2030",
                "Selected option" : "#f5002a",
            }
            config["Accent 5"] = {
                "Name" : "Purple",
                "Button" : "#b400f0",
                "User" : "#ff00ff",
                "Button highlight" : "#c040ff",
                "Selected option" : "#bc00fa",
            }
            config.write(settings)

    def theming(self,theme_sect="",accent_sect=""):
        config = configparser.ConfigParser()
        config.read(self.file_theme)
        sect = theme_sect
        theme = self.themelist[0]
        for i in self.themelist:
            if i["name"] == sect:
                theme = i
        sect = accent_sect
        accent = self.accentlist[0]
        for i in self.accentlist:
            if i["name"] == sect:
                accent = i
        return theme, accent
    
    def request(self,command):
        try:
            c = socket.socket()
            c.connect(("localhost",9999))

            command = command.strip()
            print("request",command)
            c.send(bytes(command,"utf-8"))
            resp = c.recv(1024).decode().strip()
            print("resp",resp)

            if resp[:5] == "Error" or resp[:12] == "Server error":
                return False, resp

            c.close()
            return True, resp

        except Exception as e:
            resp = "Error: " + str(e)
            print(resp)
            return False, resp

    def hashing(self,username,password,email=""):
        _user = sha256(bytes(username,"utf-8")).hexdigest()
        _pass_txt = "[user]"+username+"[pass]"+password
        _pass = sha256(bytes(_pass_txt,"utf-8")).hexdigest()
        if email == "":
            _email = ""
        else:
            _email = sha256(bytes(email,"utf-8")).hexdigest()
        return _pass, _email
    
    def regex_email(self,email):
        reg = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
        if re.fullmatch(reg,email):
            return True
        else:
            return False
        
    def regex_user(self,user):
        reg = r"[\w -]*"
        if re.fullmatch(reg,user):
            return True
        else:
            return False