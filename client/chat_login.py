import socket
import tkinter as tk
import os
import chat_settings

save = os.path.dirname(__file__)+"/chat_settings.txt"

win = tk.Tk()

delay = 1000
run = 1

'''Save file formatting by lines:
0 - Username
1 - Password
2 - Theme
3 - Accent
'''

class client():
    def __init__(self):
        try:
            with open(save,"r") as file:
                lines = file.readlines()
                print(lines)
                self.user = lines[0].strip()
                self.password = lines[1].strip()
                self.theme = lines[2].strip()
                self.accent = lines[3].strip()
        except:
            self.user = ""
            self.password = ""
            self.theme = ""
            self.accent = ""
        
        self.success = 0

        #Lists for managing widget themes
        self.ls_frame = []
        self.ls_label = []
        self.ls_entry = []
        self.ls_button = []
        self.ls_check = []

        #Widgets
        self.frame = tk.Frame(win)
        self.frame.pack()
        self.ls_frame.append(self.frame)
        self.welcome = tk.Label(self.frame,text="Welcome!")
        self.welcome.pack()
        self.ls_label.append(self.welcome)
        self.name_label = tk.Label(self.frame, text="Please write your nickname:")
        self.name_label.pack()
        self.ls_label.append(self.name_label)
        self.name = tk.Entry(self.frame,width=25,highlightthickness=0)
        self.name.insert(0,self.user)
        self.name.pack(padx=16)
        self.ls_entry.append(self.name)
        self.name_label2 = tk.Label(self.frame, text="This will be the name under which your messages will be sent")
        self.name_label2.pack(padx=16)
        self.ls_label.append(self.name_label2)

        #self.password_label = tk.Label(win, text="Password:")
        #self.password_label.pack()
        #self.password = tk.Entry(win)
        #self.password.pack()

        self.remvar = tk.IntVar()
        self.remember = tk.Checkbutton(self.frame,text="Remember me",variable=self.remvar,highlightthickness=0)
        self.remember.pack()
        self.ls_check.append(self.remember)

        if self.user != "":
            self.remvar.set(1)

        self.send = tk.Button(self.frame, text="Login", command=self.submit,highlightthickness=0)
        self.send.pack()
        self.ls_button.append(self.send)
        self.error = tk.Label(self.frame,fg="red")
        self.error.pack()
        self.ls_label.append(self.error)

        self.setting = chat_settings.settings()
        self.theming()

        if self.user == "":
            self.join()
            self.c.close()
        else:
            self.submit()
    
    def join(self):
        try:
            self.c = socket.socket()
            self.c.connect(("localhost",9999))
            return 1
        except:
            self.error["text"] = "Could not connect to server"
            return 0

    def submit(self):
        self.error["text"] = ""
        self.user = self.name.get().strip()
        if self.join():
            self.c.send(bytes("login\n"+self.user,"utf-8"))
            resp = self.c.recv(1024).decode()
            with open(save,"w") as file:
                if self.remvar.get():
                    file.write(self.user)
                    file.write("\n")
                else:
                    file.write("\n")
                file.write("\n"+self.theme)
                file.write("\n"+self.accent)
            if resp == "OK":
                self.success = 1
                win.destroy()
            else:
                self.error["text"] = resp
            self.c.close()

    def theming(self):
        #Function used to theme local settings window

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
        col_high_text = theme["high_text"]

        col_button = accent["button"]
        col_user = accent["user"]
        col_button_high = accent["button_high"]
        col_select = accent["selected"]

        #Update widget colours
        for i in self.ls_frame:
            i["bg"] = col_bg
            i["borderwidth"] = 1
        for i in self.ls_label:
            i["bg"] = col_bg
            i["fg"] = col_text
        for i in self.ls_button:
            i["bg"] = col_button
            i["fg"] = col_text
            i["activebackground"] = col_button_high
            i["activeforeground"] = col_text
        for i in self.ls_check:
            i["bg"] = col_bg
            i["fg"] = col_text
            i["selectcolor"] = col_button
            i["activebackground"] = col_high
            i["activeforeground"] = col_text
        '''self.msg_field = tk.Text(self.frame,
                                 height=3,
                                 bg=self.col_msg,
                                 fg=self.col_text,
                                 highlightthickness=0,
                                 insertbackground=self.col_text)'''
        for i in self.ls_entry:
            i["bg"] = col_msg
            i["fg"] = col_text
            i["insertbackground"] = col_text
            i["selectforeground"] = col_text
            i["selectbackground"] = col_high

        self.error["fg"] = "red"


def main():
    global success
    cl = client()

    win.mainloop()
    if cl.success:
        return cl.user
    else:
        return ""
    
if __name__ == "__main__": print("Please run the program through chat_main.py")