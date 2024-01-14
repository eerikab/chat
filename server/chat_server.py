import socket
import os

directory = os.path.dirname(__file__)+"/chatserverlog.txt"
s = socket.socket()
print("socket created")

s.bind(("localhost",9999))

s.listen(5)
print("Waiting for connection")

while True:
    c, addr = s.accept()
    msg = c.recv(1024).decode()
    print("Connected with ", addr, msg)
 
    #c.send(bytes(msg,"utf-8"))

    with open(directory,"a") as file:
        if msg != "default":
            file.write("\n"+msg)

    if msg != "login":
        with open(directory,"r") as file:
            msgs = file.readlines()
            text = str(len(msgs))
            c.send(bytes(text,"utf-8"))
            for line in msgs:
                c.send(bytes(line,"utf-8"))

    c.close()