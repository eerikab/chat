import socket
import tkinter as tk
#from tkinter import ttk
import chat_settings
import os

delay = 1000
run = 1
save = os.path.dirname(__file__)+"/chat_settings.txt"


class client():
    def __init__(self,user) -> None:
        #Read theming settings from file
        try:
            with open(save,"r") as file:
                lines = file.readlines()
                print(lines)
                self.theme = lines[2].strip()
                self.accent = lines[3].strip()
        except:
            self.theme = ""
            self.accent = ""

        #Create lists for easier configuration of widgets
        self.ls_frame = []
        self.ls_text = []
        self.ls_label = []
        self.ls_button = []

        self.left = tk.Frame(win)
        self.left.pack(side="left",fill="y")

        self.right = tk.Frame(win)
        self.right.pack(side="right",fill="both",expand=1)

        self.text_frame = tk.Frame(self.right)
        #self.text_frame.pack(fill="both",side="top",expand=1)

        #self.label = tk.Label(self.text_frame,height=1,background="white",anchor="sw",justify="left",fg=col_text,bg=bg2, wraplength=300)
        self.label = tk.Text(self.right,
                             height=1,
                             highlightthickness=0)
        #self.label.bind('<Configure>', lambda e: self.label.config(wraplength=self.label.winfo_width()))
        self.label.pack(fill="both",side="top",expand=1)
        self.ls_text.append(self.label)

        self.frame = tk.Frame(self.right)
        self.frame.pack(fill="x",side="bottom")
        #self.frame.grid(column=0,row=1)
        self.ls_frame.append(self.frame)

        self.name = user

        self.error = tk.Label(self.frame)
        self.error.pack()
        self.ls_label.append(self.error)

        #self.name = tk.Entry(self.frame,bg=textbox,fg=col_text)
        #self.name.pack()

        self.message_label = tk.Label(self.frame, text="Message:")
        self.message_label.pack()
        self.ls_label.append(self.message_label)

        self.msg_field = tk.Text(self.frame,
                                 height=3,
                                 highlightthickness=0,)
        self.msg_field.pack(fill="x",padx=16)
        self.ls_text.append(self.msg_field)

        self.send = tk.Button(self.frame,
                              text="Send message",
                              command=self.post,
                              highlightthickness=0)
        self.send.pack(pady=8)
        self.ls_button.append(self.send)

        self.settings = tk.Button(self.left, 
                                  text="Settings",
                                  highlightthickness=0,
                                  command=self.guiset)
        self.settings.pack(side="bottom",padx=16,pady=16)
        self.ls_button.append(self.settings)

        self.close = tk.Button(self.left, 
                                  text="Log out",
                                  highlightthickness=0,
                                  command=self.logout)
        self.close.pack(side="bottom",padx=16)
        self.ls_button.append(self.close)

        self.name_label = tk.Label(self.left, text="Logged in as\n"+self.name)
        self.name_label.pack(side="bottom",pady=8)
        self.ls_label.append(self.name_label)

        self.msgs = []

        self.settings = chat_settings.settings(self)
        self.theming()

        win.geometry("800x600")
        win.minsize(640,360)

        win.after(100,self.receive)


    def start(self):
        if self.join():
        #self.request("default")
            self.receive()

    def request(self,cmd):
        try:
            self.c = socket.socket()
            self.c.connect(("localhost",9999))

            print("request",cmd)
            self.c.send(bytes(cmd,"utf-8"))
            resp = self.c.recv(1024).decode()
            print("resp",resp)

            self.c.close()
            return resp

        except Exception as e:
            self.error["text"] = "Error: " + str(e)

    def post(self):
        _name = self.name
        _msg = self.msg_field.get(1.0,"end").strip()
        print(_name,_msg)
        if _name != "" and _msg != "":
            _text = _name + ":\n" + _msg
            _text = _text.strip()

            print(_text)
            self.request("post\n"+_text)
            self.msg_field.delete(1.0,tk.END)
            self.receive()


    def receive(self):
        
        count = int(self.request("num"))
        if count != len(self.msgs):
            for i in range(count):
                if i >= len(self.msgs):
                    self.msgs.append(self.request("get\n"+str(i)))

            print(len(self.msgs))
            num = 0
            self.label.delete(1.0,tk.END)
            for i in self.msgs:
                for j in i.split("\n"):
                    line = j.strip()
                    if True:#num % 2 == 1:
                        if line[0:3] == "usr":
                            line = "\n"+line[3:]
                            self.label.insert(tk.END,line+" ","User")
                        else:
                            if line[0:3] == "msg":
                                line = line[3:]
                            self.label.insert(tk.END,line+"\n")

                    #self.label.tag_add("User"+str(num),str(num)+".0",str(num+1)+"2.0")
                    num += 1
            
            self.label.see(tk.END)

    def on_exit(self):
        global run 
        run = 0
        win.destroy()

    def guiset(self):
        print("self guiset")
        self.theme, self.accent = self.settings.guiset()

        #self.theming()

    def theming(self):
        #Function used to theme local settings window
        #Update selected theme name
        try:
            with open(save,"r") as file:
                lines = file.readlines()
                print(lines)
                self.theme = lines[2].strip()
                self.accent = lines[3].strip()
        except:
            self.theme = ""
            self.accent = ""
        
        print("theming",self.theme,self.accent)

        #Get theme colours
        theme, accent = self.settings.theming(self.theme,self.accent)
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
        for i in self.ls_label:
            i["bg"] = col_bg
            i["fg"] = col_text
        for i in self.ls_button:
            i["bg"] = col_button
            i["fg"] = col_text
            i["activebackground"] = col_button_high
            i["activeforeground"] = col_text
        for i in self.ls_text:
            i["bg"] = col_msg
            i["fg"] = col_text
            i["insertbackground"] = col_text
            i["selectforeground"] = col_text
            i["selectbackground"] = col_high

        #Update widgets with other colours
        self.error["fg"] = "red"
        self.label.tag_configure("User",foreground=col_user)
        self.left["bg"] = col_side
        self.label["bg"] = col_textbox
        self.name_label["bg"] = col_side

    def logout(self):
        global ret
        win.destroy()
        with open(save,"w") as file:
            file.write("\n")
            file.write("\n"+self.theme)
            file.write("\n"+self.accent)
        ret = 1

def main(user):
    global win, ret
    ret = 0
    win = tk.Tk()
    win.title("Chat")
    client(user)

    #win.after(delay, read)
    win.mainloop()

    return ret

if __name__ == "__main__": print("Please run the program through chat_main.py")