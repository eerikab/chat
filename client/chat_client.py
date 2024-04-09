import socket
import tkinter as tk
#from tkinter import ttk
import chat_settings
import os
import configparser

delay = 1000
run = 1
directory = os.path.dirname(__file__)
save = directory+"/chat_settings.txt"
cachedir = directory+"/cache/"


class client():

    def __init__(self,user,master,password,userid) -> None:

        #Initialise window
        self.win = tk.Toplevel(master.win)
        self.win.title("Chat")

        self.font = directory+"/fonts/Cantarell.ttf"
        self.font_bold = directory+"/fonts/Cantarell-Bold.ttf"

        self.master = master

        self.name = user
        self.userid = str(userid)
        self.password = password

        #Create lists for easier configuration of widgets
        self.ls_frame = []
        self.ls_text = []
        self.ls_label = []
        self.ls_button = []
        self.ls_scroll = []

        #Create widgets
        self.left = tk.Frame(self.win)
        self.left.pack(side="left",fill="y")

        self.right = tk.Frame(self.win)
        self.right.pack(side="right",fill="both",expand=1)

        self.text_frame = tk.Frame(self.right)
        self.text_frame.pack(fill="both",expand=1)
        self.ls_frame.append(self.text_frame)

        #self.label = tk.Label(self.text_frame,height=1,background="white",anchor="sw",justify="left",fg=col_text,bg=bg2, wraplength=300)
        self.label = tk.Text(self.text_frame,
                             height=1,
                             width=1,
                             highlightthickness=0,
                             borderwidth=0,
                             )
        #self.label.bind('<Configure>', lambda e: self.label.config(wraplength=self.label.winfo_width()))
        self.label.pack(fill="both",side="left",expand=1)
        self.ls_text.append(self.label)

        self.scrollbar = tk.Scrollbar(self.text_frame,
                                      command=self.label.yview,
                                      borderwidth=0,
                                      highlightthickness=0)
        self.scrollbar.pack(side="right",fill="y")

        self.label.config(yscrollcommand=self.scrollbar.set)

        self.frame = tk.Frame(self.right)
        self.frame.pack(fill="x",side="bottom")
        self.ls_frame.append(self.frame)

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
                                 highlightthickness=0)
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
                                  command=self.guiset,
                                  width=8)
        self.settings.pack(side="bottom",padx=16,pady=16)
        self.ls_button.append(self.settings)

        self.close = tk.Button(self.left, 
                                  text="Log out",
                                  highlightthickness=0,
                                  command=self.logout,
                                  width=8)
        self.close.pack(side="bottom",padx=16)
        self.ls_button.append(self.close)

        self.name_label = tk.Label(self.left, text="Logged in as\n"+self.name,width=15)
        self.name_label.pack(side="bottom",pady=8)
        self.ls_label.append(self.name_label)

        self.msgs = dict()
        self.msg_min = -1
        self.msg_max = -1
        self.users = dict()

        self.settings = chat_settings.settings(self)
        self.theming()

        self.win.geometry("800x600")
        self.win.minsize(640,360)
        self.win.protocol('WM_DELETE_WINDOW', self.on_exit)

        self.check_min = 0
        self.check_max = 0
        self.win.after(100,self.timed)

        #Load cache
        os.makedirs(directory+"/cache",exist_ok=True)
        try:
            config = configparser.ConfigParser()
            config.read(cachedir+"main.txt")

            i = 0
            while True:
                sect = "msg"+str(i)
                if config.has_section(sect):
                    msg = dict(config.items(sect))
                    self.msgs[str(i)] = msg
                    i += 1
                    print("Loaded cache",sect)

                    user = msg["user"]
                    if not user in self.users:
                        self.users[user] = self.request("user",user)

                else:
                    break

        except:
            pass

    def request(self,cmd="",txt=""):
        try:
            self.c = socket.socket()
            self.c.connect(("localhost",9999))

            msg = cmd + "\n" + self.userid + "\n" + self.password + "\n" + txt
            msg = msg.strip()
            print("request",msg)
            self.c.send(bytes(msg,"utf-8"))
            resp = self.c.recv(1024).decode().strip()
            print("resp",resp)

            if len(resp) > 12 and resp[:5] == "Error" or resp[:12] == "Server error":
                self.error["text"] = resp

            self.c.close()
            return resp

        except Exception as e:
            self.error["text"] = "Error: " + str(e)

    def post(self):
        _msg = self.msg_field.get(1.0,"end").strip()
        if _msg != "":
            self.request("post",_msg)
            self.msg_field.delete(1.0,tk.END)
            self.receive()

    def receive(self):
        count = int(self.request("num"))

        if count != self.msg_max+1:
            #Get up to 50 messages at a time
            msg_max = count-1
            msg_min = count-51
            if msg_min < 0:
                msg_min = 0
            self.chkmsg(msg_min,msg_max)

        elif self.scrollbar.get()[0] == 0 and self.msg_min > 0:
            msg_max = self.msg_min-1
            msg_min = msg_max-51
            if msg_min < 0:
                msg_min = 0
            self.chkmsg(msg_min,msg_max)

        else: return

        print(len(self.msgs))

        num = 0
        self.label.delete(1.0,tk.END)
        for i in range(self.msg_min,self.msg_max+1):
            msg = self.msgs[str(i)]

            self.label.insert(tk.END,"\n"+self.users[msg["user"]]+" ","User")
            self.label.insert(tk.END,msg["date"][:16]+"\n","Date")
            self.label.insert(tk.END,msg["msg"]+"\n")
        
        self.label.see(tk.END)

    def chkmsg(self,msg_min,msg_max):
        with open(cachedir+"main.txt","a") as file:
            config = configparser.ConfigParser()
            i = msg_max
            while i >= msg_min:
                sect = str(i)
                try:
                    msg = self.msgs[sect]
                except Exception as e:
                    #print(str(e))
                    get = self.request("get",str(i))
                    get = get.split("\n")
                    print(get)
                    msg = ""
                    for j in get[2:]:
                        msg += j+"\n"
                    msg = msg.strip()
                    md = {
                        "user" : get[0],
                        "date" : get[1],
                        "msg" : msg
                    }
                    self.msgs[sect] = md

                    user = md["user"]
                    if not user in self.users:
                        self.users[user] = self.request("user",user)

                    config["msg"+sect] = md
                if i > self.msg_max:
                    self.msg_max = i
                if i < self.msg_min or self.msg_min == -1:
                    self.msg_min = i

                i -= 1

            config.write(file)


    def on_exit(self):
        try:
            self.settings.win.destroy()
        except:
            pass

        self.win.destroy()
        self.master.win.destroy()

    def guiset(self):
        print("self guiset")
        self.settings.guiset()

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
                self.apply_theme = int(lines[4].strip())
        except:
            self.theme = ""
            self.accent = ""
            self.apply_theme = 1
        
        print("theming",self.theme,self.accent)
        for i in [self.ls_button,self.ls_label,self.ls_text]:
            for j in i:
                j["font"] = self.font + " 10"

        if self.apply_theme:
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
            for i in self.ls_button:
                i.config(bg = col_button,
                         fg = col_text,
                         activebackground = col_button_high,
                         activeforeground = col_text)
            for i in self.ls_text:
                i.config(bg = col_msg,
                         fg = col_text,
                         insertbackground = col_text,
                         selectforeground = col_text,
                         selectbackground = col_high)

            self.scrollbar.config(bg=col_side,
                                  troughcolor=col_textbox,
                                  activebackground=col_high
                                  )

            #Update widgets with other colours
            self.error["fg"] = "red"
            self.label.tag_configure("User",foreground=col_user,font=self.font+" 10 bold")
            self.label.tag_configure("Date",foreground=col_comment)
            self.left["bg"] = col_side
            self.label["bg"] = col_textbox
            self.name_label["bg"] = col_side

    def timed(self):
        self.receive()
        self.win.after(2000,self.timed)

    def logout(self):
        self.win.destroy()
        with open(save,"w") as file:
            file.write("\n")
            file.write("\n"+self.theme)
            file.write("\n"+self.accent)
            file.write("\n"+str(self.apply_theme))
        self.master.login()

def main(user,master,password,userid):
    client(user,master,password,userid)

if __name__ == "__main__": print("Please run the program through chat_main.py")