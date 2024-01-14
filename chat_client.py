import socket
import tkinter as tk
from tkinter import ttk

delay = 1000
run = 1

win = tk.Tk()

class client():

    def __init__(self) -> None:
        self.label = tk.Label(width=100,height=20,background="white",anchor="nw",justify="left")
        self.label.pack()

        self.name_label = tk.Label(win, text="Username:")
        self.name_label.pack()

        self.name = ttk.Entry(win)
        self.name.pack()

        self.name_label = ttk.Label(win, text="Message:")
        self.name_label.pack()

        self.msg_field = tk.Text(win,height=3)
        self.msg_field.pack()

        self.send = ttk.Button(win, text="Send message", command=self.post)
        self.send.pack()

        win.after(1000,self.start)

    def start(self):
        self.c = socket.socket()
        self.c.connect(("localhost",9999))

        self.c.send(bytes("default","utf-8"))
        self.receive()

    def post(self):
        _name = self.name.get()
        _msg = self.msg_field.get(1.0,"end")
        _text = _name + ": " + _msg
        _text = _text.strip()

        self.c = socket.socket()
        self.c.connect(("localhost",9999))

        print(_text)
        self.c.send(bytes("post","utf-8"))
        self.c.send(bytes(_text,"utf-8"))
        self.receive()

    def receive(self):
        num = int(self.c.recv(1024).decode())
        
        text = ""
        for i in range(num):
            msg = "\n\n" + self.c.recv(1024).decode().strip()
            text += msg
        text = text.strip()
        self.label['text'] = text
        #c.close()

    def read(self):
        c = socket.socket()
        c.connect(("localhost",9999))

        if run:
            get = c.recv().decode()
            print("loop")
            win.after(delay,self.read)
        else:
            win.destroy()

        c.close()

    def on_exit(self):
        global run 
        run = 0
        win.destroy()

client()

#win.after(delay, read)
win.mainloop()