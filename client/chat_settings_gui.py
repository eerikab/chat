import tkinter as tk
import os
import chat_settings
import chat_widgets as cw

'''Settings window for client app'''

class guiset():
    def __init__(self,master="",window=""):
        #Theming
        self.settings = chat_settings.settings()
        self.file_settings = os.path.dirname(__file__)+"/chat_settings.txt"
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

        self.master = master
        if self.master != "":
            self.user = self.master.name

        self.themelist = self.settings.themelist
        self.accentlist = self.settings.accentlist
        cw.theme_init(self)

        self.font = os.path.dirname(__file__)+"/fonts/Cantarell.ttf"
        self.font_bold = os.path.dirname(__file__)+"/fonts/Cantarell-Bold.ttf"

        self.win.title("Chat settings")
        self.theme_var = tk.StringVar(self.win)
        self.theme_var.set(self.themelist[0]["name"])
        self.accent_var = tk.StringVar(self.win)
        self.accent_var.set(self.accentlist[0]["name"])
        self.check_var = tk.IntVar(self.win)
        self.check_var.set(self.theme_apply)
        self.page = tk.StringVar(self.win,value="Appearance")

        #Widgets
        self.left = cw.frame(self,self.win,side="left",fill="y")
        self.right = cw.frame(self,self.win,side="right",fill="both",expand=1)

        self.button_theme = cw.radio(self,self.left, 
                                        text="Appearance", 
                                        value="Appearance", 
                                        variable=self.page,
                                        padiy=4,
                                        width=16,
                                        command=self.switch
                                        )
        self.button_acc = cw.radio(self,self.left, 
                                        text="Account", 
                                        value="Account", 
                                        variable=self.page,
                                        padiy=4,
                                        width=16,
                                        command=self.switch
                                        )
        self.button_about = cw.radio(self,self.left, 
                                        text="About", 
                                        value="About", 
                                        variable=self.page,
                                        padiy=4,
                                        width=16,
                                        command=self.switch
                                        )

        button_cancel = cw.button(self,self.left,
                                text="Close",
                                command=self.gui_close,
                                width=9,
                                side="bottom",
                                pady=16,
                                padx=8)

        self.page_theme()
        self.page_account()
        self.page_about()

        self.inloop = 1
        self.themed = 0

        self.local_theming()

        self.win.geometry("560x440")
        self.win.minsize(320,240)

        if __name__ == "__main__":
            self.win.mainloop()
    
    def page_theme(self):
        self.frame_theme = cw.frame(self,self.right)
        frame = self.frame_theme
        cw.label(self,frame,text="Theme:")
        for i in self.themelist:
            name = i["name"]
            theme_select = cw.radio(self,frame, 
                                        text=name, 
                                        value=name, 
                                        variable=self.theme_var,
                                        padiy=4,
                                        width=20,
                                        command=self.local_theming
                                        )
            if name == self.theme:
                self.theme_var.set(name)
        

        cw.label(self,frame,text="Accent Color:")
        for i in self.accentlist:
            name = i["name"]
            accent_select = cw.radio(self,frame, 
                                        text=name, 
                                        value=name, 
                                        variable=self.accent_var,
                                        padiy=4,
                                        width=20,
                                        command=self.local_theming
                                        )
            if name == self.accent:
                self.accent_var.set(name)

        cw.check(self,frame,variable=self.check_var,text="Apply theming",command=self.local_theming,pady=8)

        self.field = cw.text(self,frame,width=50,height=3,padx=16,borderwidth=0)
        self.field.insert(tk.END,"User ","User")
        self.field.insert(tk.END,"2024-04-10 00:45","Date")
        self.field.insert(tk.END,"\nSample message")
        
        self.error = cw.label(self,frame)

        button_ok = cw.button(self,frame,
                            text="Save changes",
                            pady=8,
                            command=self.gui_ok)

    def page_account(self):
        self.userid = "0"
        try:
            self.userid = self.master.userid
        except:
            pass

        self.frame_account = cw.frame(self,self.right)
        self.frame_account.pack_forget()
        frame = self.frame_account

        cw.label(self,frame,text="User ID: " + str(self.userid),padx=16,pady=8)
        cw.label(self,frame,text="Username: ")
        self.user_change = cw.entry(self,frame,highlightthickness=0,width=30)
        self.user_change.insert(0,self.user)
        cw.comment(self,frame,text="4-32 characters; letters, numbers, spaces, \nunderscores, dashes, periods allowed")

        cw.label(self,frame,text="Change email: ")
        self.email_change = cw.entry(self,frame,highlightthickness=0,width=30)

        cw.label(self,frame,text="Change password: ")
        self.pass_change = cw.entry(self,frame,highlightthickness=0,width=30,show="*")
        cw.comment(self,frame,text="8-64 characters")

        cw.label(self,frame,text="Confirm new password: ")
        self.pass_confirm = cw.entry(self,frame,highlightthickness=0,width=30,show="*")

        cw.label(self,frame)

        cw.label(self,frame,text="Enter current password to confirm changes: ")
        self.pass_old = cw.entry(self,frame,highlightthickness=0,width=30,show="*")

        self.error_account = cw.label(self,frame)

        button_ok = cw.button(self,frame,
                            text="Save changes",
                            pady=8,
                            command=self.submit)
    
    def page_about(self):
        self.frame_about = cw.frame(self,self.right)
        self.frame_about.pack_forget()
        frame = self.frame_about
        cw.label(self,frame,text="About:",padx=16)
        cw.label(self,frame)
        cw.label(self,frame,text="Chat")
        cw.label(self,frame,text="Made by Eerik Abel")
        cw.label(self,frame,text="Offline edition")
        cw.label(self,frame,text="Version -")
        cw.label(self,frame,text="Server version -")
        cw.label(self,frame,text="Built on Python, Tkinter")

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
        pass_hash_old, email_hash = self.hashing(self.user, pass_old, email)

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
            ch, resp = self.settings.request("update\n"+self.userid+"\n"+pass_hash_old+"\nusername\n"+user)
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
            ch, resp = self.settings.request("update\n"+self.userid+"\n"+pass_hash_old+"\nemail\n"+email_hash)
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
            
            ch, resp = self.settings.request("update\n"+self.userid+"\n"+pass_hash_old+"\npassword\n"+pass_hash_new)
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

    def local_theming(self,list_frame=[],list_label=[],list_button=[],list_radio=[]):
        #Function used to theme local settings window
        if self.check_var.get() or self.themed:
            #Get theme colours
            theme, accent = cw.theming(self,self.theme_var.get(),self.accent_var.get())
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

            self.field.tag_configure("User",foreground=col_user,font=self.font+" 10 bold")
            self.field.tag_configure("Date",foreground=col_comment)
            self.error["fg"] = "red"
            self.left["bg"] = col_side

            self.error["text"] = ""
            self.themed = 1
        
        if self.check_var.get() == 0 and self.themed:
            self.error["text"] = "Please restart to disable theming"

if __name__ == "__main__":
    guiset()