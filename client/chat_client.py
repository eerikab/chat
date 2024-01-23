import socket
import tkinter as tk
from tkinter import ttk

delay = 1000
run = 1
bg1="#333333"
bg2="#1e1e1e"
col_text="#f2f2f2"
textbox="#3f3f3f"
col_button="#006aff"
col_user="#54ff00"

win = tk.Tk()

class client():

    def __init__(self,user) -> None:
        self.text_frame = tk.Frame(win,bg=bg2)
        self.text_frame.pack(fill="both",side="top",expand=1)
        #self.text_frame.grid(column=0,row=0,sticky="W")

        #self.label = tk.Label(self.text_frame,height=1,background="white",anchor="sw",justify="left",fg=col_text,bg=bg2, wraplength=300)
        self.label = tk.Text(self.text_frame,height=1,background="white",fg=col_text,bg=bg2)
        #self.label.bind('<Configure>', lambda e: self.label.config(wraplength=self.label.winfo_width()))
        self.label.pack(fill="both",expand=1,)

        self.frame = tk.Frame(win,bg=bg1)
        self.frame.pack(fill="x",side="bottom")
        #self.frame.grid(column=0,row=1)

        self.error = tk.Label(self.frame,fg="red",bg=bg1)
        self.error.pack()

        #self.name_label = tk.Label(self.frame, text="Username:",bg=bg1,fg=col_text)
        #self.name_label.pack()

        #self.name = tk.Entry(self.frame,bg=textbox,fg=col_text)
        #self.name.pack()

        self.name = user

        self.message_label = tk.Label(self.frame, text="Message:", bg=bg1, fg=col_text,)
        self.message_label.pack()

        self.msg_field = tk.Text(self.frame,height=3,bg=textbox,fg=col_text,)
        self.msg_field.pack(fill="x",padx=16)

        self.send = tk.Button(self.frame, text="Send message", command=self.post, bg=col_button, fg=col_text)
        self.send.pack(pady=8)

        self.msgs = []

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
                    self.label.tag_configure("User",foreground=col_user)
                    num += 1
            
            self.label.see(tk.END)

    def on_exit(self):
        global run 
        run = 0
        win.destroy()

def main(user):
    client(user)

    #win.after(delay, read)
    win.mainloop()

#if __name__ == "__main__":
#    main()