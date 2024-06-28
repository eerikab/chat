import tkinter as tk
import os
import chat_settings
import chat_widgets as cw

'''Login window for client app'''

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
        cw.theme_init(self)

        self.win = tk.Toplevel(master.win)
        self.win.title("Chat login")

        self.font = os.path.dirname(__file__)+"/fonts/Cantarell.ttf"
        self.font_bold = os.path.dirname(__file__)+"/fonts/Cantarell-Bold.ttf"

        self.remvar = tk.IntVar()
        self.page = tk.StringVar(value="Login")

        #Widgets
        self.left = cw.frame(self,self.win,side="left",fill="y")
        self.right = cw.frame(self,self.win,side="right",fill="both",expand=1)
        
        self.button_login = cw.radio(self,self.left, 
                                        text="Login", 
                                        value="Login", 
                                        variable=self.page,
                                        padiy=4,
                                        width=16,
                                        command=self.switch
                                        )
        self.button_reg = cw.radio(self,self.left, 
                                        text="Register", 
                                        value="Register", 
                                        variable=self.page,
                                        padiy=4,
                                        width=16,
                                        command=self.switch
                                        )

        #Pages
        self.login = login(self)
        self.register = register(self)

        self.win.geometry("480x360")
        self.win.minsize(320,240)
        self.win.protocol('WM_DELETE_WINDOW', self.close)

        self.setting = chat_settings.settings()
        self.theming()

        ch, resp = self.setting.request("default")
        if ch:
            if self.user != "":
                self.autosubmit()
        else:
            self.register.error["text"] = "Could not connect to server"
            self.login.error["text"] = "Could not connect to server"
        
    def switch(self):
        if self.page.get() == "Register":
            self.register.frame.pack()
            self.login.frame.pack_forget()
        else:
            self.login.frame.pack()
            self.register.frame.pack_forget()

    def autosubmit(self):
        self.pass_hash = self.password
        ch, resp = self.setting.request("login\n"+self.user+"\n"+self.pass_hash)
        if ch:
            try:
                self.userid = int(resp)
                self.success = 1
            except:
                self.login.error["text"] = resp
                pass
            if self.success:
                self.master.client(self.user,self.pass_hash,self.userid)
                self.win.destroy()
        else:
            self.login.error["text"] = resp

    def submit(self):
        self.login.error["text"] = ""
        self.user = self.login.entry_name.get().strip()
        self.password = self.login.entry_pass.get().strip()
        self.pass_hash, self.email_hash = self.setting.hashing(self.user,self.password)
        ch, resp = self.setting.request("login\n"+self.user+"\n"+self.pass_hash)
        if ch:
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
            except:
                self.login.error["text"] = resp
                pass
            if self.success:
                self.master.client(self.user,self.pass_hash,self.userid)
                self.win.destroy()
        else:
            self.login.error["text"] = resp

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
            ch, resp = self.setting.request("register\n"+self.user+"\n"+self.pass_hash+"\n"+self.email_hash)
            try:
                self.userid = int(resp)
                with open(save,"w") as file:
                    file.write(self.user)
                    file.write("\n"+self.pass_hash)
                    file.write("\n"+self.theme)
                    file.write("\n"+self.accent)
                    file.write("\n"+str(self.apply_theme))
                self.success = 1
            except:
                self.register.error["text"] = resp
                pass
            if self.success:
                self.master.client(self.user,self.pass_hash,self.userid)
                self.win.destroy()

    def theming(self):
        #Function used to theme local settings window
        if self.apply_theme:
            #Get theme colours
            theme, accent = cw.theming(self,self.theme,self.accent)
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
            self.left["bg"] = col_side
            self.login.error["fg"] = "red"
            self.register.error["fg"] = "red"

    def close(self):
        self.win.destroy()
        self.master.win.destroy()

class login():
    def __init__(self,master) -> None:
        global cl
        self.master = master

        self.remvar = tk.IntVar()
        #Widgets
        self.frame = cw.frame(self.master,self.master.right,fill="both")
        cw.label(self.master,self.frame,text="Welcome!",pady=8)

        cw.label(self.master,self.frame,text="Username:")
        self.entry_name = cw.entry(self.master,self.frame,width=25)
        self.entry_name.insert(0,master.user)
        
        cw.label(self.master,self.frame,text="Password:")
        self.entry_pass = cw.entry(self.master,self.frame,width=25,show="*")

        self.remember = cw.check(self.master,self.frame,text="Remember me",variable=self.remvar,command=self.master.theming)
        self.error = cw.label(self.master,self.frame)
        self.send = cw.button(self.master,self.frame, text="Log in", command=master.submit, pady=8)

class register():
    def __init__(self,master) -> None:
        global cl
        self.master = master

        self.frame = cw.frame(self.master,self.master.right)
        #self.frame.pack(fill="both")
        self.frame.pack_forget()
        
        #Widgets
        cw.label(self.master,self.frame,text="Welcome!",pady=8)
        cw.label(self.master,self.frame,text="Email:")
        self.entry_email = cw.entry(self.master,self.frame,width=25)

        cw.label(self.master,self.frame,text="Username:")
        self.entry_name = cw.entry(self.master,self.frame,width=25)
        cw.comment(self.master,self.frame,text="4-32 characters; letters, numbers, spaces, \nunderscores, dashes, periods allowed")

        cw.label(self.master,self.frame,text="Password:")
        self.entry_pass = cw.entry(self.master,self.frame,width=25,show="*")
        cw.comment(self.master,self.frame,text="8-64 characters")
        cw.label(self.master,self.frame,text="Confirm password:")
        self.pass2 = cw.entry(self.master,self.frame,width=25,show="*")

        self.error = cw.label(self.master,self.frame)
        self.send = cw.button(self.master,self.frame, text="Sign up", command=master.signup,pady=8)

def main(master):
    global cl
    cl = client(master)
    
if __name__ == "__main__": print("Please run the program through chat_main.py")