import socket
import os
#import time

print("Server initialized. Press Ctrl+Z to close")
directory = os.path.dirname(__file__)+"/chatserverlog.txt"
s = socket.socket()

s.bind(("localhost",9999))
print("Socket created")

s.listen(1)
print("Waiting for connection")

while True:
    c, addr = s.accept()
    get = c.recv(1024).decode().split("\n")
    cmd = get[0]
    print("Connected with ", addr, cmd)
 
    #c.send(bytes(msg,"utf-8"))

    if cmd == "post":
        with open(directory,"a") as file:
            for num in range(len(get)-1):
                msg = get[num+1]
                file.write("\n"+msg)

    if cmd != "login":
        with open(directory,"r") as file:
            msgs = file.readlines()
            text = ""
            for line in msgs:
                text += line+"\n"
            text.strip()
            c.send(bytes(text,"utf-8"))
            

    c.close()