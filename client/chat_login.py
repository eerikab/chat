'''Login window for client app'''

import os
import chat_settings as settings
import chat_widgets as cw
import chat_global as cg
import chat_settings_gui as csg

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
        self.master = master
        self.success = 0

        self.win = cw.window(self,cg.app_name+" login",size="560x420",minsize=(320,240))

        self.page = cw.stringvar("Login")

        #Widgets
        self.left = cw.frame(self,self.win,side="left",fill="y",bg="side")
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
        
        self.button_settings = cw.button(self, self.left, text="Settings", command=self.guiset, 
                                         side="bottom",pady=16, padx=16, width=8)
        #Pages
        self.login = login(self)
        self.register = register(self)
        self.recover = recover(self)
        self.switch()

        ch, resp = settings.request("version")
        if ch:
            cg.server_version = resp
            if cg.user != "":
                self.autosubmit()
        else:
            self.register.error.set("Could not connect to server")
            self.login.error.set("Could not connect to server")

    def switch(self):
        page = self.page.get()
        if page == "Register":
            self.register.frame.pack()
            self.login.frame.pack_forget()
            self.recover.frame.pack_forget()
            self.register.error.set("")
        elif page == "Recover":
            self.register.frame.pack_forget()
            self.login.frame.pack_forget()
            self.recover.frame.pack()
        else:
            self.login.frame.pack()
            self.register.frame.pack_forget()
            self.recover.frame.pack_forget()
            self.login.error.set("")
        self.win.title(cg.app_name + " login - " + page)

    def autosubmit(self):
        self.pass_hash = cg.password
        ch, resp = settings.request("login\n"+cg.user+"\n"+self.pass_hash)
        if ch:
            try:
                ids = resp.split("\n")
                cg.userid = ids[0]
                cg.session = ids[1]
                self.success = 1
            except:
                self.login.error.set(resp)
                pass
            if self.success:
                self.master.client()
                self.win.destroy()
        else:
            self.login.error.set(resp)

    def submit(self):
        self.login.error.set("")
        self.user = self.login.entry_name.get().strip()
        self.password = self.login.entry_pass.get().strip()
        self.pass_hash = settings.hash_password(self.user,self.password)
        ch, resp = settings.request("login\n"+self.user+"\n"+self.pass_hash)
        if ch:
            cg.remember = self.login.remember.get()
            self.client(resp)
        else:
            self.login.error.set(resp)

    def signup(self):
        self.register.error.set("")
        self.user = self.register.entry_name.get()
        self.password = self.register.entry_pass.get()
        self.pass2 = self.register.pass2.get()
        self.email = self.register.entry_email.get()
        self.pass_hash = settings.hash_password(self.user, self.password)
        self.email_hash = settings.hashing(self.email)

        if self.user == "" or self.password == "" or self.pass2 == "" or self.email == "":
            self.register.error.set("Please fill all fields")
            return
        
        if len(self.user) < 4 or len(self.user) > 32:
            self.register.error.set("Username must be 4-32 characters")
            return
        
        if len(self.password) < 8 or len(self.password) > 64:
            self.register.error.set("Password must be 8-64 characters")
            return
        
        if self.password != self.pass2:
            self.register.error.set("Passwords do not match")
            return
        
        if settings.regex_email(self.email) == False:
            self.register.error.set("Invalid email format")
            return
        
        if settings.regex_user(self.user) == False:
            self.register.error.set("Username contains invalid characters")
            return
        
        ch, resp = settings.request("register\n"+self.user+"\n"+self.pass_hash+"\n"+self.email_hash)
        if ch:
            cg.remember = 0
            self.client(resp)
        else:
            self.register.error.set(resp)

    def close(self):
        self.win.destroy()

    def guiset(self):
        self.window_settings = csg.guiset(self,self.win)

    def client(self,resp=""):
        #Destroy settings window, if exists
        try:
            self.window_settings.win.destroy()
        except:
            pass

        #Save user data and create client window
        ids = resp.split("\n")
        cg.user = self.user
        cg.userid = ids[0]
        cg.session = ids[1]
        cg.password = self.pass_hash
        print(cg.userid,cg.session)
        settings.save_user()
        self.win.destroy()
        self.master.client()

    def start_recover(self):
        self.page.set("Recover")
        self.recover.frame_email.pack()
        self.recover.frame_recover.pack_forget()
        self.recover.error_email.set("")
        self.recover.error_recover.set("")
        self.switch()

    def send_email(self):
        self.email = self.recover.entry_email.get()
        ch, resp = settings.request("email\n"+self.email)
        if ch:
            self.user = resp
            self.recover.frame_email.pack_forget()
            self.recover.frame_recover.pack()
            self.recover.error_recover.set("")
        else:
            self.recover.error_email.set(resp)

    def reset_password(self):
        rec_code = self.recover.entry_recover.get()
        self.password = self.recover.entry_pass.get()
        self.pass2 = self.recover.pass2.get()

        if rec_code == "" or self.password == "" or self.pass2 == "":
            self.recover.error_recover.set("Please fill all fields")
            return
        
        if len(self.password) < 8 or len(self.password) > 64:
            self.recover.error_recover.set("Password must be 8-64 characters")
            return
        
        if self.password != self.pass2:
            self.recover.error_recover.set("Passwords do not match")
            return
        
        if len(rec_code) != 8:
            self.recover.error_recover.set("Invalid code")
            return

        self.pass_hash = settings.hash_password(self.user, self.password)
        ch, resp = settings.request("reset\n"+rec_code+"\n"+self.email+"\n"+self.pass_hash)
        if ch:
            cg.remember = 0
            self.client(resp)
        else:
            self.recover.error_recover.set(resp)
    

class login():
    def __init__(self,master=client) -> None:
        global cl
        self.master = master

        self.frame = cw.frame(self.master,self.master.right,fill="both")
        self.frame.pack_forget()

        #Widgets
        cw.label(self.master,self.frame,text="Welcome to "+cg.app_name+"!",pady=8)
        cw.label(self.master,self.frame,text="Username:")
        self.entry_name = cw.entry(self.master,self.frame)
        self.entry_name.insert(cg.user)
        
        cw.label(self.master,self.frame,text="Password:")
        self.entry_pass = cw.entry(self.master,self.frame,show="*")

        self.remember = cw.check(self.master,self.frame,text="Remember me",command=cw.theming)
        self.error = cw.error(self.master,self.frame)
        self.send = cw.button(self.master,self.frame, text="Log in", command=master.submit, pady=8)

        cw.label_button(self.master, self.frame, text="Recover password", command=master.start_recover)
        cw.label_button(self.master, self.frame, text="Web version", url="https://eerikab.github.io/chat/")

class register():
    def __init__(self,master=client) -> None:
        global cl
        self.master = master

        self.frame = cw.frame(self.master,self.master.right)
        self.frame.pack_forget()
        
        #Widgets
        cw.label(self.master,self.frame,text="Welcome to "+cg.app_name+"!",pady=8)
        cw.label(self.master,self.frame,text="Username:")
        self.entry_name = cw.entry(self.master,self.frame)
        cw.comment(self.master,self.frame,text="4-32 characters; letters, numbers, \nunderscores, dashes, periods allowed")
        
        cw.label(self.master,self.frame,text="Email:")
        self.entry_email = cw.entry(self.master,self.frame)
        cw.comment(self.master,self.frame,text="Valid email format")

        cw.label(self.master,self.frame,text="Password:")
        self.entry_pass = cw.entry(self.master,self.frame,show="*")
        cw.comment(self.master,self.frame,text="8-64 characters")
        cw.label(self.master,self.frame,text="Confirm password:")
        self.pass2 = cw.entry(self.master,self.frame,show="*")

        self.error = cw.error(self.master,self.frame)
        self.send = cw.button(self.master,self.frame, text="Sign up", command=master.signup,pady=8)

class recover():
    def __init__(self, master=client):
        self.master = master

        self.frame = cw.frame(self.master, self.master.right)
        self.frame.pack_forget()

        cw.label(self.master, self.frame, text="Recover account",pady=8)

        self.frame_email = cw.frame(self.master, self.frame)
        cw.label(self.master,self.frame_email,text="Enter the email address linked to your account\n" 
                 "If it is valid, you will be sent a verification code")
        self.entry_email = cw.entry(self.master,self.frame_email)
        self.error_email = cw.error(self.master,self.frame_email)
        self.submit_email = cw.button(self.master,self.frame_email, text="Send",pady=8,command=master.send_email)

        self.frame_recover = cw.frame(self.master, self.frame)
        cw.label(self.master,self.frame_recover,text='An 8-digit recovery code should be sent'
                    '\nto your email address from "tickchatsprt"'
                    "\nIf you can't see it, also check the spam folder"
                    "\nThe code will expire in 20 minutes\n\nRecovery code:")
        self.entry_recover = cw.entry(self.master,self.frame_recover)
        
        cw.label(self.master,self.frame_recover,text="Set a new password:")
        self.entry_pass = cw.entry(self.master,self.frame_recover,show="*")
        cw.comment(self.master,self.frame_recover,text="8-64 characters")
        cw.label(self.master,self.frame_recover,text="Confirm new password:")
        self.pass2 = cw.entry(self.master,self.frame_recover,show="*")
        self.error_recover = cw.error(self.master,self.frame_recover)
        self.send = cw.button(self.master,self.frame_recover, text="Submit", command=master.reset_password,pady=8)



def main(master):
    global cl
    cl = client(master)
    
if __name__ == "__main__": print("Please run the program through chat_main.py")