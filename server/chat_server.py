import socket
import os
#import time

directory = os.path.dirname(__file__)+"/chatserverlog.txt"
s = socket.socket()

s.bind(("localhost",9999))
print("Server initialized. Press Ctrl+C to close")
print("Socket created")

with open(directory,"r") as file:
    msgs_full = file.readlines()

text = ""
msgs = []
for i in msgs_full:
    if i[0:3] == "usr":
        text = text.strip()
        msgs.append(text)
        text = i
    else:
        text += i
text = text.strip()
msgs.append(text)
    
print(len(msgs))
#print(msgs)

s.listen(1)
print("Waiting for connection")

def post(txt):
    c.send(bytes(txt,"utf-8"))

while True:
    c, addr = s.accept()
    get = c.recv(1024).decode().split("\n")
    cmd = get[0]
    print("Connected with ", addr, get)
 
    #c.send(bytes(msg,"utf-8"))

    if cmd == "post":
        text=""
        with open(directory,"a") as file:
            for num in range(1,len(get)):
                msg = get[num]
                if num == 1:
                    text+="usr"+msg
                    file.write("\nusr"+msg)
                else:
                    text+="\nmsg"+msg
                    file.write("\nmsg"+msg)
        msgs.append(text.strip())
        post("OK")

    elif cmd == "num":
        post(str(len(msgs)))

    elif cmd == "get":
        post(msgs[int(get[1])])

    elif cmd == "login":
        if get[1] == "":
            post("Please enter a username")
        else:
            post("OK")

    else:
        post("Error: Invalid function")


    '''if cmd != "login":
        with open(directory,"r") as file:
            msgs = file.readlines()
            text = ""
            for line in msgs:
                text += line+"\n"
            text.strip()
            c.send(bytes(text,"utf-8"))'''
            

    c.close()