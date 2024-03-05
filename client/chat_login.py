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

        #Lists for managing widget themes
        self.ls_frame = []
        self.ls_label = []
        self.ls_entry = []
        self.ls_button = []
        self.ls_check = []

        #Widgets
        self.frame = tk.Frame(self.win)
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
        self.remember = tk.Checkbutton(self.frame,text="Remember me",variable=self.remvar,highlightthickness=0,command=self.theming)
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

        self.win.protocol('WM_DELETE_WINDOW', self.close)

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
                file.write("\n"+str(self.apply_theme))
            if resp == "OK":
                self.success = 1
                self.master.client(self.user)
                self.win.destroy()
            else:
                self.error["text"] = resp
            self.c.close()

    def theming(self):
        #Function used to theme local settings window
        for i in [self.ls_button,self.ls_label,self.ls_check,self.ls_entry]:
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
                if self.remvar.get():
                    i["selectcolor"] = col_button
                else:
                    i["selectcolor"] = col_msg
                i["activebackground"] = col_high
                i["activeforeground"] = col_text
            for i in self.ls_entry:
                i["bg"] = col_msg
                i["fg"] = col_text
                i["insertbackground"] = col_text
                i["selectforeground"] = col_text
                i["selectbackground"] = col_high

            self.error["fg"] = "red"

    def close(self):
        self.win.destroy()
        self.master.win.destroy()


def main(master):
    global success
    cl = client(master)
    
if __name__ == "__main__": print("Please run the program through chat_main.py")