import os
import configparser
import tkinter as tk
from hashlib import sha256
import socket
import re

class settings():
    def __init__(self,master="") -> None:
        self.file_theme = os.path.dirname(__file__)+"/chat_themes.ini"
        self.file_settings = os.path.dirname(__file__)+"/chat_settings.txt"
        self.font = os.path.dirname(__file__)+"/fonts/Cantarell.ttf"
        self.font_bold = os.path.dirname(__file__)+"/fonts/Cantarell-Bold.ttf"
        self.master = master #Main class for responding

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

    def local_theming(self,list_frame=[],list_label=[],list_button=[],list_radio=[]):
        #Function used to theme local settings window
        for i in [self.ls_button,self.ls_label,self.ls_text,self.ls_check,self.ls_radio]:
            for j in i:
                j["font"] = self.font + " 10"
        
        if self.check_var.get() or self.themed:
            #Get theme colours
            theme, accent = self.theming(self.theme_var.get(),self.accent_var.get())
            #print("Theming",self.theme_var.get(),self.accent_var.get())
            col_bg = theme["bg"]
            col_textbox = theme["textbox"]
            col_msg = theme["msg"]
            col_side = theme["side"]
            col_text = theme["text"]
            col_high = theme["high"]
            col_comment = theme["comment"]

            col_button = accent["button"]
            col_user = accent["user"] 
            col_button_high = accent["button_high"]
            col_select = accent["selected"]

            #Update widget colours
            for i in self.ls_frame:
                i.config(bg = col_bg)
            for i in self.ls_label:
                i.config(bg = col_bg,
                         fg = col_text)
            for i in self.ls_comment:
                i.config(bg = col_bg,
                         fg = col_comment)
            for i in self.ls_button:
                i.config(bg = col_button,
                         fg = col_text,
                         activebackground = col_button_high,
                         activeforeground = col_text)
            for i in self.ls_radio:
                i.config(bg = col_msg,
                         fg = col_text,
                         activebackground = col_high,
                         activeforeground = col_text,
                         selectcolor = col_select)
            for i in self.ls_text:
                i.config(bg = col_textbox,
                         fg = col_text,
                         selectbackground = col_high,
                         selectforeground = col_text,
                         insertbackground = col_text)
            for i in self.ls_check:
                i.config(bg = col_bg,
                         fg = col_text,
                         activebackground = col_high,
                         activeforeground = col_text)
                if self.check_var.get():
                    i["selectcolor"] = col_button
                else:
                    i["selectcolor"] = col_msg
            for i in self.ls_entry:
                i.config(
                    bg = col_msg,
                    fg = col_text,
                    insertbackground = col_text,
                    selectbackground = col_high,
                    selectforeground = col_text,
                )

            self.field.tag_configure("User",foreground=col_user,font=self.font+" 10 bold")
            self.field.tag_configure("Date",foreground=col_comment)
            self.error["fg"] = "red"
            self.left["bg"] = col_side

            self.error["text"] = ""
            self.themed = 1
            
        
        if self.check_var.get() == 0 and self.themed:
            self.error["text"] = "Please restart to disable theming"

    def guiset(self,window=""):
        #Theming
        try:
            with open(self.file_settings,"r") as file:
                lines = file.readlines()
                print(lines)
                self.user = lines[0].strip()
                self.password = lines[1].strip()
                self.theme = lines[2].strip()
                self.accent = lines[3].strip()
                self.theme_apply = int(lines[4].strip())
        except:
            self.user = ""
            self.password = ""
            self.theme = ""
            self.accent = ""
            self.theme_apply = 1

        #Create window
        if window == "":
            self.win = tk.Tk()
        else:
            self.win = tk.Toplevel(window)

        if self.master != "":
            self.user = self.master.name

        self.win.title("Chat settings")
        self.theme_var = tk.StringVar(self.win)
        self.theme_var.set(self.themelist[0]["name"])
        self.accent_var = tk.StringVar(self.win)
        self.accent_var.set(self.accentlist[0]["name"])
        self.check_var = tk.IntVar(self.win)
        self.check_var.set(self.theme_apply)
        self.page = tk.StringVar(self.win,value="Appearance")

        #Lists for managing widget themes
        self.ls_frame = []
        self.ls_label = []
        self.ls_radio = []
        self.ls_button = []
        self.ls_text = []
        self.ls_check = []
        self.ls_entry = []
        self.ls_comment = []

        #print(self.theme)

        self.left = tk.Frame(self.win)
        self.left.pack(side="left",fill="y")
        self.ls_frame.append(self.left)
        self.right = tk.Frame(self.win)
        self.right.pack(side="right",fill="both",expand=1)
        self.ls_frame.append(self.right)

        self.button_theme = tk.Radiobutton(self.left, 
                                        text="Appearance", 
                                        value="Appearance", 
                                        variable=self.page,
                                        indicatoron=0,
                                        borderwidth=0,
                                        pady=4,
                                        width=16,
                                        highlightthickness=0,
                                        command=self.switch
                                        )
        self.button_theme.pack()
        self.ls_radio.append(self.button_theme)
        self.button_acc = tk.Radiobutton(self.left, 
                                        text="Account", 
                                        value="Account", 
                                        variable=self.page,
                                        indicatoron=0,
                                        borderwidth=0,
                                        pady=4,
                                        width=16,
                                        highlightthickness=0,
                                        command=self.switch
                                        )
        self.button_acc.pack()
        self.ls_radio.append(self.button_acc)
        self.button_about = tk.Radiobutton(self.left, 
                                        text="About", 
                                        value="About", 
                                        variable=self.page,
                                        indicatoron=0,
                                        borderwidth=0,
                                        pady=4,
                                        width=16,
                                        highlightthickness=0,
                                        command=self.switch
                                        )
        self.button_about.pack()
        self.ls_radio.append(self.button_about)

        button_cancel = tk.Button(self.left,
                                text="Close",
                                highlightthickness=0,
                                command=self.gui_close,
                                width=9)
        button_cancel.pack(pady=8,padx=8,side="bottom")
        self.ls_button.append(button_cancel)

        self.page_theme()
        self.page_account()
        self.page_about()

        self.inloop = 1
        self.themed = 0

        self.local_theming()

        self.win.geometry("560x440")
        self.win.minsize(320,240)

        print(self.theme_var.get(),self.accent_var.get())

        if __name__ == "__main__":
            self.win.mainloop()
    
    def page_theme(self):
        self.frame_theme = tk.Frame(self.right)
        self.frame_theme.pack()
        self.ls_frame.append(self.frame_theme)
        frame = self.frame_theme
        theme_text = tk.Label(frame,text="Theme:")
        theme_text.pack()
        self.ls_label.append(theme_text)
        for i in self.themelist:
            name = i["name"]
            theme_select = tk.Radiobutton(frame, 
                                        text=name, 
                                        value=name, 
                                        variable=self.theme_var,
                                        indicatoron=0,
                                        borderwidth=0,
                                        pady=4,
                                        width=20,
                                        highlightthickness=0,
                                        command=self.local_theming
                                        )
            theme_select.pack()
            self.ls_radio.append(theme_select)
            if name == self.theme:
                self.theme_var.set(name)
        

        accent_text = tk.Label(frame,text="Accent Color:")
        accent_text.pack()
        self.ls_label.append(accent_text)
        for i in self.accentlist:
            name = i["name"]
            accent_select = tk.Radiobutton(frame, 
                                        text=name, 
                                        value=name, 
                                        variable=self.accent_var,
                                        indicatoron=0,
                                        borderwidth=0,
                                        pady=4,
                                        width=20,
                                        highlightthickness=0,
                                        command=self.local_theming
                                        )
            accent_select.pack()
            self.ls_radio.append(accent_select)
            if name == self.accent:
                self.accent_var.set(name)

        theme_check = tk.Checkbutton(frame,variable=self.check_var,text="Apply theming",highlightthickness=0,command=self.local_theming)
        theme_check.pack(pady=8)
        self.ls_check.append(theme_check)

        self.field = tk.Text(frame,width=50,height=3,highlightthickness=0,borderwidth=0)
        self.field.insert(tk.END,"User ","User")
        self.field.insert(tk.END,"2024-04-10 00:45","Date")
        self.field.insert(tk.END,"\nSample message")
        self.field.pack(padx=16)
        self.ls_text.append(self.field)
        
        self.error = tk.Label(frame,fg="red")
        self.error.pack()
        self.ls_label.append(self.error)

        button_ok = tk.Button(frame,
                            text="Save changes",
                            highlightthickness=0,
                            command=self.gui_ok)
        button_ok.pack(pady=8)
        self.ls_button.append(button_ok)

    def page_account(self):
        self.userid = "0"
        try:
            self.userid = self.master.userid
        except:
            pass

        self.frame_account = tk.Frame(self.right)
        #self.frame_account.pack()
        self.ls_frame.append(self.frame_account)
        frame = self.frame_account
        label = tk.Label(frame,text="User ID: " + str(self.userid))
        label.pack(padx=16,pady=8)
        self.ls_label.append(label)

        label = tk.Label(frame,text="Username: ")
        label.pack()
        self.ls_label.append(label)
        self.user_change = tk.Entry(frame,highlightthickness=0,width=30)
        self.user_change.pack()
        self.ls_entry.append(self.user_change)
        self.user_change.insert(0,self.user)
        label = tk.Label(frame,text="4-32 characters; letters, numbers, spaces, \nunderscores, dashes, periods allowed")
        label.pack()
        self.ls_comment.append(label)

        label = tk.Label(frame,text="Change email: ")
        label.pack()
        self.ls_label.append(label)
        self.email_change = tk.Entry(frame,highlightthickness=0,width=30)
        self.email_change.pack()
        self.ls_entry.append(self.email_change)

        label = tk.Label(frame,text="Change password: ")
        label.pack()
        self.ls_label.append(label)
        self.pass_change = tk.Entry(frame,highlightthickness=0,width=30,show="*")
        self.pass_change.pack()
        self.ls_entry.append(self.pass_change)

        label = tk.Label(frame,text="8-64 characters")
        label.pack()
        self.ls_comment.append(label)

        label = tk.Label(frame,text="Confirm new password: ")
        label.pack()
        self.ls_label.append(label)
        self.pass_confirm = tk.Entry(frame,highlightthickness=0,width=30,show="*")
        self.pass_confirm.pack()
        self.ls_entry.append(self.pass_confirm)

        label = tk.Label(frame)
        label.pack()
        self.ls_label.append(label)

        label = tk.Label(frame,text="Enter current password to confirm changes: ")
        label.pack()
        self.ls_label.append(label)
        self.pass_old = tk.Entry(frame,highlightthickness=0,width=30,show="*")
        self.pass_old.pack()
        self.ls_entry.append(self.pass_old)

        self.error_account = tk.Label(frame)
        self.error_account.pack()
        self.ls_label.append(self.error_account)

        button_ok = tk.Button(frame,
                            text="Save changes",
                            highlightthickness=0,
                            command=self.submit)
        button_ok.pack(pady=8)
        self.ls_button.append(button_ok)
    
    def page_about(self):
        self.frame_about = tk.Frame(self.right)
        self.ls_frame.append(self.frame_about)
        frame = self.frame_about
        label = tk.Label(frame,text="About:")
        label.pack(padx=16)
        self.ls_label.append(label)
        label = tk.Label(frame)
        label.pack()
        self.ls_label.append(label)
        label = tk.Label(frame,text="Chat")
        label.pack()
        self.ls_label.append(label)
        label = tk.Label(frame,text="Made by Eerik Abel")
        label.pack()
        self.ls_label.append(label)
        label = tk.Label(frame,text="Offline edition")
        label.pack()
        self.ls_label.append(label)
        label = tk.Label(frame,text="Version 0.0")
        label.pack()
        self.ls_label.append(label)
        label = tk.Label(frame,text="Server version 0.0")
        label.pack()
        self.ls_label.append(label)
        label = tk.Label(frame,text="Built on Python, Tkinter")
        label.pack()
        self.ls_label.append(label)

    def switch(self):
        if self.page.get() == "Account":
            self.frame_theme.pack_forget()
            self.frame_account.pack()
            self.frame_about.pack_forget()
        elif self.page.get() == "About":
            self.frame_theme.pack_forget()
            self.frame_account.pack_forget()
            self.frame_about.pack()
        else:
            self.frame_theme.pack()
            self.frame_account.pack_forget()
            self.frame_about.pack_forget()

    def submit(self):
        self.error_account["text"] = "No changes made"
        user = self.user_change.get().strip()
        password = self.pass_change.get().strip()
        pass2 = self.pass_confirm.get().strip()
        email = self.email_change.get().strip()
        pass_old = self.pass_old.get().strip()

        pass_hash_new, email_hash = self.hashing(user, password, email)
        pass_hash_old, email_hash = self.hashing(user, pass_old, email)

        if pass_hash_old != self.password:
            self.error_account["text"] = "Invalid password"
            return

        #Change username
        if user != self.master.name:
            if len(user) < 4 or len(user) > 32:
                self.error_account["text"] = "Username must be 4-32 characters"
                return
            if self.regex_user(user) == False:
                self.error_account["text"] = "Username contains invalid characters"
                return
            self.c = socket.socket()
            self.c.connect(("localhost",9999))
            self.c.send(bytes("update\n"+self.userid+"\n"+pass_hash_old+"\nusername\n"+user, "utf-8"))
            resp = self.c.recv(1024).decode().strip()
            self.c.close()
            if resp == "OK":
                self.master.name = user
                self.user = user
                self.error_account["text"] = "Changes saved"
            else:
                self.error_account["text"] = resp
                return

        #Change email
        if len(email) > 0:
            if self.regex_email(email) == False:
                self.error_account["text"] = "Invalid email format"
                return
            self.c = socket.socket()
            self.c.connect(("localhost",9999))
            self.c.send(bytes("update\n"+self.userid+"\n"+pass_hash_old+"\nemail\n"+email_hash, "utf-8"))
            resp = self.c.recv(1024).decode().strip()
            self.c.close()
            if resp == "OK":
                self.error_account["text"] = "Changes saved"
            else:
                self.error_account["text"] = resp
                return

        #Change password
        if len(password) > 0:
            if len(password) > 0 and len(password) < 8:
                self.error_account["text"] = "Password must be 8-64 characters"
                return
            
            if password != pass2:
                self.error_account["text"] = "Passwords do not match"
                return
            
            self.c = socket.socket()
            self.c.connect(("localhost",9999))
            self.c.send(bytes("update\n"+self.userid+"\n"+pass_hash_old+"\npassword\n"+pass_hash_new, "utf-8"))
            resp = self.c.recv(1024).decode().strip()
            self.c.close()
            if resp == "OK":
                self.password = pass_hash_new
                self.master.password = pass_hash_new
                self.error_account["text"] = "Changes saved"
            else:
                self.error_account["text"] = resp
                return

        #Save changes
        with open(self.file_settings,"w") as file:
            file.write(user)
            file.write("\n"+pass_hash_new)
            file.write("\n"+self.theme_var.get())
            file.write("\n"+self.accent_var.get())
            file.write("\n"+str(self.check_var.get()))

    def gui_close(self):
        self.win.destroy()

    def gui_ok(self):
        user = ""
        password = ""
        #self.win.destroy()
        try:
            with open(self.file_settings,"r") as file:
                lines = file.readlines()
                user = lines[0].strip()
                password = lines[1].strip()
        finally:
            with open(self.file_settings,"w") as file:
                file.write(user)
                file.write("\n"+password)
                file.write("\n"+self.theme_var.get())
                file.write("\n"+self.accent_var.get())
                file.write("\n"+str(self.check_var.get()))
            if self.master != "":
                self.master.theming()

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

if __name__ == "__main__":
    gui = settings()
    gui.guiset()