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

win = tk.Tk()

class client():

    def __init__(self) -> None:

        self.text_frame = tk.Frame(win,bg=bg2)
        self.text_frame.pack(fill="both",side="top",expand=1)
        #self.text_frame.grid(column=0,row=0,sticky="W")

        self.label = tk.Label(self.text_frame,height=1,background="white",anchor="sw",justify="left",fg=col_text,bg=bg2, wraplength=300)
        self.label.bind('<Configure>', lambda e: self.label.config(wraplength=self.label.winfo_width()))
        self.label.pack(fill="both",expand=1,)

        self.frame = tk.Frame(win,bg=bg1)
        self.frame.pack(fill="x",side="bottom")
        #self.frame.grid(column=0,row=1)

        self.name_label = tk.Label(self.frame, text="Username:",bg=bg1,fg=col_text)
        self.name_label.pack()

        self.name = tk.Entry(self.frame,bg=textbox,fg=col_text,)
        self.name.pack()

        self.name_label = tk.Label(self.frame, text="Message:", bg=bg1, fg=col_text)
        self.name_label.pack()

        self.msg_field = tk.Text(self.frame,height=3,bg=textbox,fg=col_text)
        self.msg_field.pack(fill="x")

        self.send = tk.Button(self.frame, text="Send message", command=self.post, bg=col_button, fg=col_text)
        self.send.pack(pady=8)

        win.geometry("800x600")
        win.minsize(320,240)

        win.after(10,self.start)

    def start(self):
        self.c = socket.socket()
        self.c.connect(("localhost",9999))

        self.c.send(bytes("default","utf-8"))
        self.receive()

    def join(self):
        self.c = socket.socket()
        self.c.connect(("localhost",9999))

    def post(self):
        _name = self.name.get().strip()
        _msg = self.msg_field.get(1.0,"end").strip()
        print(_name,_msg)
        if _name != "" and _msg != "":
            _text = _name + ": " + _msg
            _text = _text.strip()

            self.join()
            print(_text)
            self.c.send(bytes("post\n"+_text,"utf-8"))
            self.receive()

    def receive(self):
        #num = int(self.c.recv(1024).decode())
        
        text = ""
        #for i in range(num):
        #    msg = "\n" + self.c.recv(1024).decode().strip()
        #    text += msg
        msgs = self.c.recv(1024).decode().split("\n")
        print(msgs)

        num = 0
        for i in msgs:
            #if i[0] + i[1] == "\n":
            #    i = i[1,-1]
            if num % 2 == 0:
                text += "\n"+i
            num += 1
        text = text.strip()
        self.label['text'] = text
        #c.close()

    def on_exit(self):
        global run 
        run = 0
        win.destroy()

client()

#win.after(delay, read)
win.mainloop()