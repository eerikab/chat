import socket
import tkinter as tk
import os
import chat_settings

save = os.path.dirname(__file__)+"/chat_settings.txt"

delay = 1000
run = 1

'''Save file formatting by lines:
0 - Username
1 - Password
2 - Theme
3 - Accent
4 - Apply theming
'''

class client():
    def __init__(self,master):
        try:
            with open(save,"r") as file:
                lines = file.readlines()
                print(lines)
                self.user = lines[0].strip()
                self.password = lines[1].strip()
                self.theme = lines[2].strip()
                self.accent = lines[3].strip()
                self.apply_theme = int(lines[4].strip())
        except:
            self.user = ""
            self.password = ""
            self.theme = ""
            self.accent = ""
            self.apply_theme = 1
        
        self.master = master
        self.success = 0


        self.win = tk.Toplevel(master.win)
        self.win.title("Chat login")

        self.font = os.path.dirname(__file__)+"/fonts/Cantarell.ttf"
        self.font_bold = os.path.dirname(__file__)+"/fonts/Cantarell-Bold.ttf"

        self.remvar = tk.IntVar()
        self.page = tk.StringVar(value="Login")

        #Lists for managing widget themes
        self.ls_frame = []
        self.ls_label = []
        self.ls_entry = []
        self.ls_button = []
        self.ls_check = []
        self.ls_radio = []
        self.ls_comment = []

        #Widgets
        self.left = tk.Frame(self.win)
        self.left.pack(side="left",fill="y")
        self.ls_frame.append(self.left)
        self.right = tk.Frame(self.win)
        self.right.pack(side="right",fill="both",expand=1)
        self.ls_frame.append(self.right)
        
        self.button_login = tk.Radiobutton(self.left, 
                                        text="Login", 
                                        value="Login", 
                                        variable=self.page,
                                        indicatoron=0,
                                        borderwidth=0,
                                        pady=4,
                                        width=16,
                                        highlightthickness=0,
                                        command=self.switch
                                        )
        self.button_login.pack()
        self.ls_radio.append(self.button_login)
        self.button_reg = tk.Radiobutton(self.left, 
                                        text="Register", 
                                        value="Register", 
                                        variable=self.page,
                                        indicatoron=0,
                                        borderwidth=0,
                                        pady=4,
                                        width=16,
                                        highlightthickness=0,
                                        command=self.switch
                                        )
        self.button_reg.pack()
        self.ls_radio.append(self.button_reg)

        #Pages
        self.login = login(self)
        self.register = register(self)

        self.win.geometry("480x360")
        self.win.minsize(320,240)
        self.win.protocol('WM_DELETE_WINDOW', self.close)

        self.setting = chat_settings.settings()
        self.theming()

        if self.user == "":
            if self.join():
                self.c.send(bytes("Default","utf-8"))
            self.c.close()
        else:
            self.autosubmit()
    
    def join(self):
        try:
            self.c = socket.socket()
            self.c.connect(("localhost",9999))
            return 1
        except:
            self.login.error["text"] = "Could not connect to server"
            self.register.error["text"] = "Could not connect to server"
            return 0
        
    def switch(self):
        if self.page.get() == "Register":
            self.register.frame.pack()
            self.login.frame.pack_forget()
        else:
            self.login.frame.pack()
            self.register.frame.pack_forget()

    def autosubmit(self):
        self.pass_hash = self.password
        if self.join():
            self.c.send(bytes("login\n"+self.user+"\n"+self.pass_hash, "utf-8"))

            resp = self.c.recv(1024).decode()
            try:
                self.userid = int(resp)
                self.success = 1
                self.master.client(self.user,self.pass_hash,self.userid)
                self.win.destroy()
            except:
                self.login.error["text"] = resp
                pass
            self.c.close()

    def submit(self):
        self.login.error["text"] = ""
        self.user = self.login.entry_name.get().strip()
        self.password = self.login.entry_pass.get().strip()
        self.pass_hash, self.email_hash = self.setting.hashing(self.user,self.password)
        if self.join():
            self.c.send(bytes("login\n"+self.user+"\n"+self.pass_hash, "utf-8"))

            resp = self.c.recv(1024).decode()
            try:
                self.userid = int(resp)
                with open(save,"w") as file:
                    if self.login.remvar.get():
                        file.write(self.user)
                        file.write("\n"+self.pass_hash)
                    else:
                        file.write("\n")
                    file.write("\n"+self.theme)
                    file.write("\n"+self.accent)
                    file.write("\n"+str(self.apply_theme))
                self.success = 1
                self.master.client(self.user,self.pass_hash,self.userid)
                self.win.destroy()
            except:
                self.login.error["text"] = resp
                pass
            self.c.close()

    def signup(self):
        self.register.error["text"] = ""
        self.user = self.register.entry_name.get().strip()
        self.password = self.register.entry_pass.get().strip()
        self.pass2 = self.register.pass2.get().strip()
        self.email = self.register.entry_email.get().strip()
        self.pass_hash, self.email_hash = self.setting.hashing(self.user, self.password, self.email)

        if self.user == "" or self.password == "" or self.pass2 == "" or self.email == "":
            self.register.error["text"] = "Please fill all fields"
            return
        
        if len(self.user) < 4 or len(self.user) > 32:
            self.register.error["text"] = "Username must be 4-32 characters"
            return
        
        if len(self.password) < 8 or len(self.password) > 64:
            self.register.error["text"] = "Password must be 8-64 characters"
            return
        
        if self.password != self.pass2:
            self.register.error["text"] = "Passwords do not match"
            return
        
        if self.setting.regex_email(self.email) == False:
            self.register.error["text"] = "Invalid email format"
            return
        
        if self.setting.regex_user(self.user) == False:
            self.register.error["text"] = "Username contains invalid characters"
            return
        
        if self.join():
            self.c.send(bytes("register\n"+self.user+"\n"+self.pass_hash+"\n"+self.email_hash, "utf-8"))

            resp = self.c.recv(1024).decode().strip()
            try:
                self.userid = int(resp)
                with open(save,"w") as file:
                    file.write(self.user)
                    file.write("\n"+self.pass_hash)
                    file.write("\n"+self.theme)
                    file.write("\n"+self.accent)
                    file.write("\n"+str(self.apply_theme))
                self.success = 1
                self.master.client(self.user,self.pass_hash,self.userid)
                self.win.destroy()
            except:
                self.register.error["text"] = resp
                pass
            self.c.close()

    def theming(self):
        #Function used to theme local settings window
        for i in [self.ls_button,self.ls_label,self.ls_check,self.ls_entry,self.ls_radio]:
            for j in i:
                j["font"] = self.font + " 10"
        
        if self.apply_theme:
            #Get theme colours
            theme, accent = self.setting.theming(self.theme,self.accent)
            self.theme = theme["name"]
            self.accent = accent["name"]
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
            self.left["bg"] = col_side
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
            for i in self.ls_check:
                i.config(bg = col_bg,
                         fg = col_text,
                         activebackground = col_high,
                         activeforeground = col_text)
                if self.login.remvar.get():
                    i["selectcolor"] = col_button
                else:
                    i["selectcolor"] = col_msg
            for i in self.ls_entry:
                i.config(bg = col_msg,
                         fg = col_text,
                         insertbackground = col_text,
                         selectforeground = col_text,
                         selectbackground = col_high)
            for i in self.ls_radio:
                i.config(bg = col_msg,
                         fg = col_text,
                         activebackground = col_high,
                         activeforeground = col_text,
                         selectcolor = col_select)

            self.login.error["fg"] = "red"
            self.register.error["fg"] = "red"

    def close(self):
        self.win.destroy()
        self.master.win.destroy()

class login():
    def __init__(self,master) -> None:
        global cl
        self.master = master

        self.frame = tk.Frame(self.master.right)
        self.frame.pack(fill="both")
        self.master.ls_frame.append(self.frame)
        
        #Widgets
        label = tk.Label(self.frame,text="Welcome!")
        label.pack(pady=8)
        self.master.ls_label.append(label)
        label = tk.Label(self.frame,text="Username:")
        label.pack()
        self.master.ls_label.append(label)

        self.entry_name = tk.Entry(self.frame,highlightthickness=0,width=25)
        self.entry_name.pack()
        self.master.ls_entry.append(self.entry_name)
        self.entry_name.insert(0,master.user)

        label = tk.Label(self.frame,text="Password:")
        label.pack()
        self.master.ls_label.append(label)
        
        self.entry_pass = tk.Entry(self.frame,highlightthickness=0,width=25,show="*")
        self.entry_pass.pack()
        self.master.ls_entry.append(self.entry_pass)

        self.remvar = tk.IntVar()
        self.remember = tk.Checkbutton(self.frame,text="Remember me",variable=self.remvar,highlightthickness=0,command=self.master.theming)
        self.remember.pack()
        self.master.ls_check.append(self.remember)

        self.error = tk.Label(self.frame)
        self.error.pack()
        self.master.ls_label.append(self.error)

        self.send = tk.Button(self.frame, text="Log in", command=master.submit,highlightthickness=0)
        self.send.pack(pady=8)
        self.master.ls_button.append(self.send)

class register():
    def __init__(self,master) -> None:
        global cl
        self.master = master

        self.frame = tk.Frame(self.master.right)
        #self.frame.pack(fill="both")
        self.master.ls_frame.append(self.frame)
        
        #Widgets
        label = tk.Label(self.frame,text="Welcome!")
        label.pack(pady=8)
        self.master.ls_label.append(label)
        label = tk.Label(self.frame,text="Email:")
        label.pack()
        self.master.ls_label.append(label)

        self.entry_email = tk.Entry(self.frame,highlightthickness=0,width=25)
        self.entry_email.pack()
        self.master.ls_entry.append(self.entry_email)

        label = tk.Label(self.frame,text="Username:")
        label.pack()
        self.master.ls_label.append(label)

        self.entry_name = tk.Entry(self.frame,highlightthickness=0,width=25)
        self.entry_name.pack()
        self.master.ls_entry.append(self.entry_name)

        label = tk.Label(self.frame,text="4-32 characters; letters, numbers, spaces, \nunderscores, dashes, periods allowed")
        label.pack()
        self.master.ls_comment.append(label)

        label = tk.Label(self.frame,text="Password:")
        label.pack()
        self.master.ls_label.append(label)
        
        self.entry_pass = tk.Entry(self.frame,highlightthickness=0,width=25,show="*")
        self.entry_pass.pack()
        self.master.ls_entry.append(self.entry_pass)

        label = tk.Label(self.frame,text="8-64 characters")
        label.pack()
        self.master.ls_comment.append(label)

        label = tk.Label(self.frame,text="Confirm password:")
        label.pack()
        self.master.ls_label.append(label)
        
        self.pass2 = tk.Entry(self.frame,highlightthickness=0,width=25,show="*")
        self.pass2.pack()
        self.master.ls_entry.append(self.pass2)

        self.error = tk.Label(self.frame)
        self.error.pack()
        self.master.ls_label.append(self.error)

        self.send = tk.Button(self.frame, text="Sign up", command=master.signup,highlightthickness=0)
        self.send.pack(pady=8)
        self.master.ls_button.append(self.send)

def main(master):
    global cl
    cl = client(master)
    
if __name__ == "__main__": print("Please run the program through chat_main.py")