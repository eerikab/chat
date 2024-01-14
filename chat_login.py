import socket
import tkinter as tk

win = tk.Tk()

delay = 1000
run = 1

def submit():
    c = socket.socket()
    c.connect(("localhost",9999))

    c.send(bytes("login","utf-8"))
    c.send(bytes(name.get(),"utf-8"))
    c.send(bytes(password.get(),"utf-8"))

name_label = tk.Label(win, text="Username:")
name_label.pack()
name = tk.Entry(win)
name.pack()

password_label = tk.Label(win, text="Password:")
password_label.pack()
password = tk.Entry(win)
password.pack()

send = tk.Button(win, text="Login", command=submit)
send.pack()

win.mainloop()