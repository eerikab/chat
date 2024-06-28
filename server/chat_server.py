import socket
import os
import datetime
import hashlib
import configparser
import random
import re

'''Server code, stores data and hadles communication
Keep seperate from the client'''

#Data directories
chatdir = os.path.dirname(__file__)+"/data/chat/"
os.makedirs(chatdir, exist_ok=True) #Why should the folder already existing cause an error by default?
userdir = os.path.dirname(__file__)+"/data/users/"
os.makedirs(userdir, exist_ok=True)

#Following file paths only work if there is only 1 chat room or 1 user file
chat_general = chatdir + "main.ini"
userdir += "users.ini"

#Create networking socket
s = socket.socket()
print("Starting up server. Press Ctrl+C to close")
s.bind(("localhost",9999))
print("Socket created\nReading user list")

#Read user data
config = configparser.ConfigParser()
config.read(userdir)
users = dict()
for i in config.sections():
    users[i] = dict(config.items(i))

print(str(len(users)) + " Users loaded\nReading messages")

#Get the amount of posts
posts = 0
while True:
    try:
        config = configparser.ConfigParser()
        path = chatdir+"post"+str(posts)+".ini"
        print(path)
        config.read(path)
        if config.has_section("msg0"):
            posts += 1
        else:
            print("Else")
            break
    except Exception as e:
        print("Exception",e)
        break

print(str(posts) + " posts found")

print("Init done")
s.listen(3)
print("Waiting for connections")

def time():
    return str(datetime.datetime.now(datetime.UTC))[:22]

def respond(txt):
    print("Response", txt)
    c.send(bytes(txt,"utf-8"))

def hashing(txt):
    return hashlib.sha256(bytes(txt,"utf-8")).hexdigest()

def validate(get):
    user = get[1]
    password = get[2]
    config = configparser.ConfigParser()
    config.read(userdir)
    if config[user]["password"] == hashing(password):
        return True
    else:
        return False
    
def regex_user(user):
        reg = r"[\w .-]*"
        if re.fullmatch(reg,user):
            return "OK"
        else:
            return "Error: Username contains invalid characters"

def commands(get):
    cmd = get[0]
    global posts

    #Responses
    if cmd == "message":
        user = get[1]
        msg = ""
        date = time()
        post = chatdir+get[3]+".ini"

        if not validate(get):
            return "Error: Invalid credentials"
        
        for i in get[4:]:
            msg += i+"\n"
        msg = msg.strip()

        config = configparser.ConfigParser()
        config.read(post)
        length = len(config)-1

        with open(post,"a") as file:
            config = configparser.ConfigParser()
            md = {
                "user" : user,
                "date" : date,
                "msg" : msg
            }
            
            config["msg"+str(length)] = md
            config.write(file)
            return "OK"

    elif cmd == "post":
        user = get[1]
        msg = ""
        date = time()

        if not validate(get):
            return "Error: Invalid credentials"
        
        for i in get[3:]:
            msg += i+"\n"
        msg = msg.strip()

        with open(chatdir+"post"+str(posts)+".ini","a") as file:
            config = configparser.ConfigParser()
            md = {
                "user" : user,
                "date" : date,
                "msg" : msg
            }

            posts += 1
            config["msg0"] = md
            config.write(file)
            return "OK"

    elif cmd == "num":
        post = get[3]
        if not validate(get):
            return "Error: Invalid credentials"
        config = configparser.ConfigParser()
        config.read(chatdir + post + ".ini")
        return str(len(config)-1)
    
    elif cmd == "postnum":
        if not validate(get):
            return "Error: Invalid credentials"
        return str(posts)

    elif cmd == "get":
        post = get[3]
        if not validate(get):
            return "Error: Invalid credentials"
        config = configparser.ConfigParser()
        config.read(chatdir + post + ".ini")
        ls = config[get[4]]
        msg = ls["user"] + "\n" + ls["date"] + "\n" + ls["msg"]
        
        return msg
    
    elif cmd == "default":
        return "OK"
    
    elif cmd == "user":
        if not validate(get):
            return "Error: Invalid credentials"
        if get[3] in users:
            return users[get[3]]["username"]
        else:
            return "[user " + get[3] + "]"

    elif cmd == "login":
        user = get[1]
        password = hashing(get[2])
        for i in users:
            j = users[i]
            if user == j["username"] and password == j["password"]:
                return i
        return "Invalid username or password"

    elif cmd == "register":
        user = get[1]
        password = hashing(get[2])
        email = hashing(get[3])

        if len(user) < 4 or len(user) > 32:
            return "Error: Username must be 4-32 characters"
        
        reg = regex_user(user)
        if reg != "OK":
            return reg

        for i in users:
            j = users[i]
            if j["username"] == user:
                return "Error: Username taken"
            if j["email"] == email:
                return "Error: Email taken"
        
        #Random 16-digit user ID
        userid = str(random.randrange(1_000_000_000_000_000, 9_999_999_999_999_999))

        while userid in users:
            userid = str(random.randrange(1_000_000_000_000_000, 9_999_999_999_999_999))
        users[userid] = {"username" : user,
                         "password" : password,
                         "email" : email}
        
        #Save new user
        config = configparser.ConfigParser()
        with open(userdir,"a") as file:
            config[userid] = users[userid]
            config.write(file)

        return userid
    
    elif cmd == "update":
        userid = get[1]
        mode = get[3]
        new = get[4]

        #Error checking
        if not validate(get):
            return "Error: Invalid credentials"

        if mode == "username":
            if len(new) < 4 or len(new) > 32:
                return "Error: Username must be 4-32 characters"
            
            reg = regex_user(new)
            if reg != "OK":
                return reg

            for i in users:
                if i != userid:
                    if users[userid]["username"] == new:
                        return "Error: Username taken"
            
            users[userid][mode] = new

        elif mode == "password":
            users[userid][mode] = hashing(new)

        elif mode == "email":
            for i in users:
                if i != userid:
                    if users[userid]["email"] == new:
                        return "Error: Email taken"
            users[userid][mode] = hashing(new)

        else:
            return "Error: Invalid type of data"
        
        #Update user
        config = configparser.ConfigParser()
        with open(userdir,"r") as file:
            config.read(file)
        with open(userdir,"w") as file:
            config[userid] = users[userid]
            config.write(file)

        return "OK"
    
    return "Error: Invalid function"

while True:
    #Get client request
    c, addr = s.accept()
    try:
        get = c.recv(1024).decode().split("\n")
        print("Connected with ", addr, time(), get)
        resp = commands(get)
        respond(resp)


    except Exception as e:
        try:
            respond("Server error: "+str(e))
        except Exception as e:
            print("Failed connection with client")
            
    c.close()