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
        if master == "":
            close = 1
        else:
            close = 0
        self.win = cw.window(self,"Chat settings","640x480",(480,360),close_all=close)

        self.master = master
        if self.master != "":
            self.user = self.master.name

        self.themelist = self.settings.themelist
        self.accentlist = self.settings.accentlist

        self.theme_var = cw.stringvar(self.themelist[0]["name"])
        self.accent_var = cw.stringvar(self.accentlist[0]["name"])
        self.page = cw.stringvar("Appearance")

        #Widgets
        self.left = cw.frame(self,self.win,side="left",fill="y",bg="side")
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

        cw.button(self,self.left,
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

        if __name__ == "__main__":
            cw.root.mainloop()
    
    def page_theme(self):
        self.frame_theme = cw.frame(self,self.right)
        frame = self.frame_theme
        cw.label(self,frame,text="Theme:")
        for i in self.themelist:
            name = i["name"]
            cw.radio(self,frame, 
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
            cw.radio(self,frame, 
                    text=name, 
                    value=name, 
                    variable=self.accent_var,
                    padiy=4,
                    width=20,
                    command=self.local_theming
                    )
            if name == self.accent:
                self.accent_var.set(name)

        self.check_apply = cw.check(self,frame,text="Apply theming",command=self.local_theming,pady=8)
        self.check_apply.variable.set(self.theme_apply)

        self.field = cw.text(self,frame,width=50,height=3,padx=16,borderwidth=0)
        self.field.insert("User ","User")
        self.field.insert("2024-04-10 00:45","Date")
        self.field.insert("\nSample message")
        
        self.error = cw.error(self,frame)

        cw.button(self,frame,
                    text="Save changes",
                    pady=8,
                    command=self.gui_ok)

    def page_account(self):
        try:
            self.userid = self.master.userid
        except:
            self.userid = "0"

        self.frame_account = cw.frame(self,self.right)
        self.frame_account.pack_forget()
        frame = self.frame_account

        cw.label(self,frame,text="User ID: " + str(self.userid),padx=16,pady=8)
        cw.label(self,frame,text="Username: " + self.user)

        cw.button(self,frame,text="Change username",width=15,pady=8,command=self.change_name)
        cw.button(self,frame,text="Change password",width=15,pady=8,command=self.change_password)
        cw.button(self,frame,text="Change email",width=15,pady=8,command=self.change_email)

        self.frame_change = cw.frame(self,frame)
        self.frame_change.pack_forget()

        self.account_widgets()
        self.change_current = ""
    
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

    def account_widgets(self):
        frame = self.frame_change

        self.label_change_new = cw.label(self,frame,text="Change email: ")
        self.change_new = cw.entry(self,frame,highlightthickness=0,width=30)

        self.comment_change = cw.comment(self,frame,text="8-64 characters")

        frame_confirm = cw.frame(self,frame)
        self.frame_confirm = cw.frame(self,frame_confirm)

        cw.label(self,self.frame_confirm,text="Confirm new password: ")
        self.change_confirm = cw.entry(self,self.frame_confirm,highlightthickness=0,width=30,show="*")

        cw.label(self,self.frame_confirm)

        cw.label(self,frame,text="Enter current password to confirm changes: ")
        self.change_old_pass = cw.entry(self,frame,highlightthickness=0,width=30,show="*")

        self.error_account = cw.label(self,frame)

        cw.button(self,frame,
                text="Save changes",
                pady=8,
                command=self.submit)
        
        self.change_new.get()
        self.change_confirm.get()
        self.change_old_pass.get()
        
    def change_standard(self):
        self.frame_change.pack()
        self.change_new.clear()
        self.change_confirm.clear()
        self.change_old_pass.clear()
        
    def change_name(self):
        self.label_change_new.set("Change username:")
        self.comment_change.set("4-32 characters; letters, numbers, - _ . allowed")
        self.frame_confirm.pack_forget()
        self.change_current = "username"
        self.change_standard()
        self.change_new.insert(self.user)
        self.change_new.uncensor()

    def change_password(self):
        self.label_change_new.set("Change password:")
        self.comment_change.set("8-64 characters")
        self.frame_confirm.pack()
        self.change_current = "password"
        self.change_standard()
        self.change_new.censor()

    def change_email(self):
        self.label_change_new.set("Change email:")
        self.comment_change.set("Must be in a valid format")
        self.frame_confirm.pack_forget()
        self.change_current = "email"
        self.change_standard()
        self.change_new.uncensor()
        
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
        self.error_account.set("No changes made")
        new = self.change_new.get()
        confirm = self.change_confirm.get()
        password = self.change_old_pass.get()

        pass_hash_old = self.settings.hash_password(self.user, password)

        if pass_hash_old != self.password:
            self.error_account.set("Invalid password")
            return

        #Change username
        if self.change_current == "username":
            if len(new) < 4 or len(new) > 32:
                self.error_account.set("Username must be 4-32 characters")
                return
            if self.settings.regex_user(new) == False:
                self.error_account.set("Username contains invalid characters")
                return
            
            pass_hash_new = self.settings.hash_password(new, password)
            ch, resp = self.settings.request("update\n"+self.userid+"\n"+pass_hash_old+"\nusername\n"+new+"\n"+pass_hash_new)
            if ch:
                self.master.name = new
                self.user = new
                self.password = pass_hash_new
                self.master.password = self.password
                self.error_account.set("Changes saved")
            else:
                self.error_account.set(resp)
                return

        #Change email
        if self.change_current == "email" and len(new) > 0:
            email_hash = self.settings.hashing(new)
            if self.settings.regex_email(new) == False:
                self.error_account.set("Invalid email format")
                return
            ch, resp = self.settings.request("update\n"+self.userid+"\n"+pass_hash_old+"\nemail\n"+email_hash)
            if ch:
                self.error_account.set("Changes saved")
            else:
                self.error_account.set(resp)
                return

        #Change password
        if self.change_current == "password" and len(new) > 0:
            if len(new) > 64 or len(new) < 8:
                self.error_account.set("Password must be 8-64 characters")
                return
            
            if new != confirm:
                self.error_account.set("Passwords do not match")
                return
            
            pass_hash_new = self.settings.hash_password(self.user, new)
            
            ch, resp = self.settings.request("update\n"+self.userid+"\n"+pass_hash_old+"\npassword\n"+pass_hash_new)
            if resp == "OK":
                self.password = pass_hash_new
                self.master.password = pass_hash_new
                self.error_account.set("Changes saved")
            else:
                self.error_account.set(resp)
                return

        #Save changes
        with open(self.file_settings,"w") as file:
            if self.check_apply.variable.get():
                file.write(self.user)
                file.write("\n"+self.password)
            else:
                file.write("\n")
            file.write("\n"+self.theme_var.get())
            file.write("\n"+self.accent_var.get())
            file.write("\n"+str(self.check_apply.variable.get()))

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
                file.write("\n"+str(self.check_apply.variable.get()))
            if self.master != "":
                self.master.theming()

    def local_theming(self,list_frame=[],list_label=[],list_button=[],list_radio=[]):
        #Function used to theme local settings window
        if self.check_apply.variable.get() or self.themed:
            #Get theme colours
            cw.theming(self,self.theme_var.get(),self.accent_var.get())

            self.error.set("")
            self.themed = 1
        
        if self.check_apply.variable.get() == 0 and self.themed:
            self.error.set("Please restart to disable theming")

if __name__ == "__main__":
    guiset()