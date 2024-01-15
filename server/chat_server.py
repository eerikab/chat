import socket
import os
import time

print("Server initialized. Press Ctrl+Z to close")
directory = os.path.dirname(__file__)+"/chatserverlog.txt"
s = socket.socket()

s.bind(("localhost",9999))
print("Socket created")

s.listen(1)
print("Waiting for connection")

while True:
    c, addr = s.accept()
    msg = c.recv(1024).decode()
    print("Connected with ", addr, msg)
 
    #c.send(bytes(msg,"utf-8"))

    with open(directory,"a") as file:
        if msg == "post":
            file.write("\n"+msg)

    if msg != "login":
        with open(directory,"r") as file:
            msgs = file.readlines()
            text = str(len(msgs))
            c.send(bytes(text,"utf-8"))
            for line in msgs:
                c.send(bytes(line,"utf-8"))
                

    c.close()