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
                    "name" : config.get(sect,"name"),
                    "bg" : config.get(sect,"background"),
                    "textbox" : config.get(sect,"textbox"),
                    "msg" : config.get(sect,"messagebox"),
                    "side" : config.get(sect,"sidebar"),
                    "text" : config.get(sect,"text"),
                    "high" : config.get(sect,"highlight"),
                    "comment" : config.get(sect,"comment")
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
                    "name" : config.get(sect,"name"),
                    "button" : config.get(sect,"button"),
                    "user" : config.get(sect,"user"),
                    "button_high" : config.get(sect,"button_highlight"),
                    "selected" : config.get(sect,"selected_option"),
                    "error" : config.get(sect,"error"),
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
                "background" : "#ececec",
                "textbox" : "#fafafa",
                "messagebox" : "#dcdcdc",
                "sidebar" : "#dcdcdc",
                "text" : "#202020",
                "highlight" : "#c8c8c8",
                "comment" : "#8c8c8c"
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
        return {**theme,**accent} 
    
    def request(self,command):
        try:
            c = socket.socket()
            c.connect(("localhost",9999))

            command = command.strip()
            #print("request",command)
            c.send(bytes(command,"utf-8"))
            resp = c.recv(1024).decode().strip()
            #print("resp",resp)

            if resp[:5] == "Error" or resp[:12] == "Server error":
                return False, resp

            c.close()
            return True, resp

        except Exception as e:
            resp = "Error: " + str(e)
            print(resp)
            return False, resp

    def hashing(self,name):
        return sha256(bytes(name,"utf-8")).hexdigest()
    
    def hash_password(self,username,password):
        _pass_txt = "[user]"+username+"[pass]"+password
        _pass = sha256(bytes(_pass_txt,"utf-8")).hexdigest()
        return _pass
    
    def regex_email(self,email):
        reg = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
        if re.fullmatch(reg,email):
            return True
        else:
            return False
        
    def regex_user(self,user):
        reg = r"[\w -_.]*"
        if re.fullmatch(reg,user):
            return True
        else:
            return False
        
    def load_line(self, lines, line, integer=False, default=""):
        try:
            var = lines[line].strip()
        except:
            var = default

        return var
        
    def load_user(self):
        with open(self.file_settings,"r") as file:
            lines = file.readlines()
            print(lines)
            
            self.user = self.load_line(lines, 0)
            self.password = self.load_line(lines, 1)
            self.theme = self.load_line(lines, 2)
            self.accent = self.load_line(lines, 3)
            self.apply_theme = self.load_line(lines, 4, True, 1)

    def save_user(self):
        with open(self.file_settings,"w") as file:
            if self.apply_theme:
                file.write(self.user)
                file.write("\n"+self.password)
            else:
                file.write("\n")
            file.write("\n"+self.theme)
            file.write("\n"+self.accent)
            file.write("\n"+str(self.apply_theme))