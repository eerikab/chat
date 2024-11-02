'''Server code, stores data and handles communication
Keep separate from the client'''

#import socketserver
import os
import datetime
import hashlib
import configparser
import random
import re
import sys
import asyncio
from websockets.server import serve

HOST, PORT = "localhost", 9000

#Versions
version = "0.0.0"
py_version = sys.version.split()[0]
print("Python version",sys.version)

#Data directories
dir_chat = os.path.dirname(__file__)+"/data/chat/"
dir_user = os.path.dirname(__file__)+"/data/users/"
os.makedirs(dir_user, exist_ok=True) #Why should the folder already existing cause an error by default?

dir_post = dir_chat + "posts/" #Posts
dir_msg = dir_chat + "msg/" #Direct messages
dir_group = dir_chat + "group/" #Group chats
os.makedirs(dir_post, exist_ok=True)
os.makedirs(dir_msg, exist_ok=True)
os.makedirs(dir_group, exist_ok=True)

#Following file paths only work if there is only 1 chat room or 1 user file
dir_general = dir_chat + "main.ini"
dir_user += "users.ini"

#Read user data
config = configparser.ConfigParser()
config.read(dir_user)
users = dict()
for i in config.sections():
    users[i] = dict(config.items(i))

print(str(len(users)) + " Users loaded\nReading messages")

#Get the amount of posts
posts = 0
while True:
    try:
        config = configparser.ConfigParser()
        path = dir_post+"post"+str(posts)+".ini"
        config.read(path)
        if config.has_section("msg0"):
            posts += 1
        else:
            break
    except Exception as e:
        break

print(str(posts) + " posts found")


#Functions
def time():
    return str(datetime.datetime.now(datetime.timezone.utc))[:22]

def hashing(txt):
    return hashlib.sha256(bytes(txt,"utf-8")).hexdigest()

def validate(get):
    user = get[1]
    password = get[2]
    config = configparser.ConfigParser()
    config.read(dir_user)
    if config[user]["password"] == hashing(password):
        return True
    else:
        return False
    
def randnum():
    #Random 16 digit number in string format
    return str(random.randrange(1_000_000_000_000_000, 9_999_999_999_999_999))
    
def regex_user(user):
        reg = r"[\w .-]*"
        if re.fullmatch(reg,user):
            return "OK"
        else:
            return "Error: Username contains invalid characters"
        
def user_exists(name,key="username"):
    for i in users:
        j = users[i]
        if j[key] == name:
            return i
    
    return ""

def get_directory(file="",userid=""):
    #Find the appropriate directory based on filename
    if file[:4] == "post":
        #Post files start with "post", followed by index
        return dir_post + file + ".ini"
    elif len(file) == 16 and file.isdigit():
        #Direct message names are composed of both user IDs, smaller first
        #Here, userid is caller and file is callee
        if int(file) < int(userid):
            chat_id = file + userid
        else:
            chat_id = userid + file
        return dir_msg + chat_id + ".ini"
    
    else:
        #Misc stuff defaults to the parent directory
        return dir_chat + file + ".ini"

def update_users():
    config = configparser.ConfigParser()
    for i in users:
        config[i] = users[i]
    with open(dir_user,"w") as file:
        config.write(file)

#Responses
def commands(get):
    cmd = get[0]
    global posts

    if cmd == "message":
        user = get[1]
        msg = ""
        date = time()
        post = get[3]

        post = get_directory(post,user)

        if not validate(get):
            return "Error: Invalid credentials"
        
        for i in get[4:]:
            msg += i+"\n"
        msg = msg.strip()

        config = configparser.ConfigParser()
        config.read(post)

        if "users" in config:
            length = len(config)-2
        else:
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

        with open(dir_post+"post"+str(posts)+".ini","a") as file:
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
        post = get_directory(get[3],get[1])
        if not validate(get):
            return "Error: Invalid credentials"
        config = configparser.ConfigParser()
        config.read(post)
        if "users" in config:
            return str(len(config)-2)
        else:
            return str(len(config)-1)
    
    elif cmd == "postnum":
        if not validate(get):
            return "Error: Invalid credentials"
        return str(posts)

    elif cmd == "get":
        post = get_directory(get[3],get[1])
        if not validate(get):
            return "Error: Invalid credentials"
        config = configparser.ConfigParser()
        config.read(post)
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
        return "Error: Invalid username or password"

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
        userid = randnum()

        while userid in users:
            userid = randnum()
        users[userid] = {"username" : user,
                         "password" : password,
                         "email" : email}
        
        #Save new user
        update_users()

        return userid
    
    elif cmd == "update":
        userid = get[1]
        mode = get[3]
        new_raw = get[4]

        #Error checking
        if not validate(get):
            return "Error: Invalid credentials"

        if mode == "username":
            pw = get[5]
            new = new_raw

            if len(new) < 4 or len(new) > 32:
                return "Error: Username must be 4-32 characters"
            
            reg = regex_user(new)
            if reg != "OK":
                return reg
            
            if users[userid][mode] == new:
                return "Error: No changes made"
            
            if user_exists(new):
                return "Error: Username taken"
            
            users[userid][mode] = new
            users[userid]["password"] = hashing(pw)

        elif mode == "password":
            new = hashing(new_raw)

            if users[userid][mode] == new:
                return "Error: No changes made"
            
            users[userid][mode] = new

        elif mode == "email":
            new = hashing(new_raw)

            if users[userid][mode] == new:
                return "Error: No changes made"
            if user_exists(new,"email"):
                return "Error: Email taken"
            
            users[userid][mode] = new

        else:
            return "Error: Invalid type of data"
        
        #Update user
        update_users()

        return "OK"
    
    elif cmd == "add_contact":
        if not validate(get):
            return "Error: Invalid credentials"
        
        user = get[1] #ID of caller user
        other_user = get[3] #Name of second user

        other_id = user_exists(other_user)
        if not other_id:
            return "Error: User not found"

        chat_path = get_directory(other_id,user)

        if os.path.exists(chat_path):
            return("Error: User already in contacts")
        
        #Add users to list
        i = 0
        while "msg"+str(i) in users[user]:
            i += 1
        users[user]["msg"+str(i)] = other_id

        i = 0
        while "msg"+str(i) in users[other_id]:
            i += 1
        users[other_id]["msg"+str(i)] = user

        #Add users to chat data, smaller ID first
        with open(chat_path,"w") as file:
            config = configparser.ConfigParser()
            if int(user) < int(other_id):
                config["users"] = {
                    "user1" : user,
                    "user2" : other_id
                }
            else:
                config["users"] = {
                    "user1" : other_id,
                    "user2" : user
                }

            config.write(file)

        update_users()
        
        return "Contact added"
    
    elif cmd == "contacts":
        if not validate(get):
            return "Error: Invalid credentials"
        
        user = get[1]

        i = 0
        text = ""
        while "msg"+str(i) in users[user]:
            text += users[user]["msg"+str(i)] + "\n"
            i += 1

        return text.strip()
    
    elif cmd == "version":
        return version
    
    print(cmd)

    return "Error: Invalid function " + str(cmd)

'''#TCP socket server - old
class tcp_handler(socketserver.BaseRequestHandler)  :
    #Get client request
    def respond(self,txt):
        if len(txt) > 1024:
            txt = "Server error: response too long"
        print("Response", txt, "\n")
        self.request.sendall(bytes(txt,"utf-8"))

    def handle(self):
        try:
            print(self.request)
            get = self.request.recv(1024).decode().split("\n")
            print("Connected with ", self.client_address, time(), get)
            resp = commands(get)
            self.respond(resp)

        except Exception as e:
            try:
                self.respond("Server error: "+str(e))
            except Exception as e:
                print("Failed connection with client")'''

#Create networking socket
print("Starting up server. Press Ctrl+C to close")

'''with socketserver.TCPServer((HOST,PORT),tcp_handler) as server:  
    print("Socket created\nWaiting for connections")
    server.serve_forever()
'''

async def handle(websocket):
    async for message in websocket:
        get = message.split("\n")
        print("Connected",get)
        try:
            resp = commands(get)
        except Exception as e:
            resp = "Server error: " + str(e)
        print("Response",resp)
        await websocket.send(resp)

async def main():
    async with serve(handle, HOST, PORT):
        print("WebSocket created\nWaiting for connections")
        await asyncio.get_running_loop().create_future()  # run forever

asyncio.run(main())