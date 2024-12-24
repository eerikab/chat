'''Server code, stores data and handles communication
Keep separate from the client'''

#import socketserver
import os
import datetime
import hashlib
import random
import re
import sys
import asyncio
from websockets.server import serve
import sqlite3
import traceback

HOST, PORT = "localhost", 9000

#Versions
version = "0.0.0"
py_version = sys.version.split()[0]
print("Python version",sys.version)

#Data directories
dir_data = os.path.dirname(__file__)+"/data/"
#Why should the folder already existing cause an error by default?
os.makedirs(dir_data, exist_ok=True) 
dir_db = dir_data + "data.db"

#Functions
def time():
    '''Return current time in UTC'''
    return str(datetime.datetime.now(datetime.timezone.utc))[:22]

def hashing(txt):
    '''SHA256 hash on string'''
    return hashlib.sha256(bytes(txt,"utf-8")).hexdigest()

def hash_password(userid, password):
    '''Hash password with userid and additional data'''
    pass_txt = "[user]"+userid+"[pass]"+password
    return hashlib.sha256(bytes(pass_txt,"utf-8")).hexdigest()

def randnum():
    '''Random 16-digit number in string format'''
    id = ""
    for i in range(16):
        id += str(random.randint(0,9))
    return id
    
def regex_user(user):
    '''Check for invalid characters in username'''
    reg = r"[\w .-]*"
    if re.fullmatch(reg,user):
        return "OK"
    else:
        return "Error: Username contains invalid characters"
    
def db_connect(statement=""):
    '''Communicate with SQL database
    Currently using built-in SQLite functionality'''
    try:
        with sqlite3.connect(dir_db) as conn:
            cursor = conn.cursor()
            cursor.execute(statement)
            return cursor.fetchone()
            
    except sqlite3.OperationalError as e:
        print("Failed to open database: ", e)
        return ("Server error: " + str(e))

def validate(get):
    '''Verify user identity through userid and hashed password'''
    try:
        user = get[1]
        password = get[2]
        row = db_connect(f"SELECT password FROM USERS WHERE userid='{user}';")
        if row[0] == hash_password(user,password):
            return True
        else:
            return False
    except:
        return False
    
def user_exists(name="",key="name"):
    '''Check if username or email is taken in the database'''
    user = db_connect(f'''SELECT userid FROM Users 
                WHERE LOWER({key})='{name.lower()}';''')
    if user:
        return user[0]
    else:
        return ""

def get_directory(file="",userid=""):
    '''Find the appropriate table based on chatroom'''
    if file[:4].lower() == "post":
        #Post files start with "Post", followed by index
        return "Post" + file[4:]
    elif len(file) == 16 and file.isdigit():
        #Direct message names are composed of both user IDs, smaller first
        #Here, userid is caller and file is callee
        if int(file) < int(userid):
            return "Room" + file + userid
        else:
            return "Room" + userid + file
    else:
        #Misc stuff defaults to the parent directory
        return file

def check_in_room(room_name="",id=""):
    '''Check if user has access to room
    Private message rooms are composed of two 16-digit user IDs'''
    if len(room_name) < 36:
        return True
    elif db_connect(f'''SELECT * FROM Contacts{id}
        WHERE room="{room_name}"'''):
        return True
    else:
        return False
    
def table_exists(table):
    '''Check if table exists in database'''
    return db_connect(f'''SELECT name FROM sqlite_master 
                WHERE type='table' AND name="{table}";''')
    
def create_chat_table(room):
    '''Create a chat room in database'''
    #Statements modifying the database should return an empty tuple
    #If a value is returned, something went wrong
    return db_connect(
        '''CREATE TABLE IF NOT EXISTS ''' + room + ''' (
            id INTEGER PRIMARY KEY,
            user TEXT NOT NULL,
            date DATE NOT NULL,
            msg TEXT NOT NULL,
            status TEXT
        );'''
    )

def post_count():
    '''Get the amount of posts sent'''
    posts = 0
    while True:
        try:
            if table_exists(f"Post{posts+1}"):
                posts += 1
            else:
                break
        except Exception as e:
            break
    return posts


# RESPONSES

def commands(get):
    cmd = get[0]

    if cmd == "message":
        user = get[1]
        msg = ""
        date = time()

        if not validate(get):
            return "Error: Invalid credentials"
        
        post = get_directory(get[3],get[1])
        
        for i in get[4:]:
            msg += i+"\n"
        msg = msg.strip()

        if len(msg) > 500:
            return "Error: Message has to be max 500 characters"

        if not check_in_room(post,get[1]):
            return "Error: No access to room"
        
        sql = db_connect(f'''INSERT INTO {post}(user,date,msg)
                   VALUES('{user}','{date}','{msg}')''')
        if sql:
            return sql[0]

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

        if len(msg) > 500:
            return "Error: Message has to be max 500 characters"

        table = "Post" + str(post_count() + 1)
        sql = create_chat_table(table)
        if sql:
            return sql[0]
        
        sql = db_connect(f'''INSERT INTO {table}(user,date,msg)
                   VALUES('{user}','{date}','{msg}')''')
        if sql:
            return sql[0]
        
        return "OK"

    elif cmd == "num":
        if not validate(get):
            return "Error: Invalid credentials"
        
        post = get_directory(get[3],get[1])

        if not check_in_room(post,get[1]):
            return "Error: No access to room"
        
        return db_connect("SELECT COUNT(*) FROM " + post)[0]
    
    elif cmd == "postnum":
        if not validate(get):
            return "Error: Invalid credentials"
        return str(post_count())

    elif cmd == "get":
        if not validate(get):
            return "Error: Invalid credentials"

        post = get_directory(get[3],get[1])

        if not check_in_room(post,get[1]):
            return "Error: No access to room"

        ls = db_connect(f'''SELECT * FROM {post} WHERE id='{int(get[4])}';''')
        msg = ls[1] + "\n" + ls[2] + "\n" + ls[3]
        
        return msg
    
    elif cmd == "user":
        if not validate(get):
            return "Error: Invalid credentials"
        user = db_connect(f"SELECT name FROM Users WHERE userid='{get[3]}';")
        if user:
            return user[0]
        else:
            return "[user " + get[3] + "]"

    elif cmd == "login":
        user = get[1]
        password = get[2]
        userid = db_connect(
            f'''SELECT userid FROM Users
                WHERE name='{user}' OR email='{hashing(user)}';'''
        )

        if userid:
            if db_connect(
                f'''SELECT userid FROM Users
                WHERE (name='{user}' OR email='{hashing(user)}')
                AND password='{hash_password(userid[0],password)}';'''
            ) or "error" in userid[0]:
                return userid[0]
        
        return "Error: Invalid username or password"

    elif cmd == "register":
        user = get[1]
        password = get[2]
        email = hashing(get[3])

        if len(user) < 4 or len(user) > 32:
            return "Error: Username must be 4-32 characters"
        
        reg = regex_user(user)
        if reg != "OK":
            return reg
        
        if db_connect(f"SELECT * FROM Users WHERE name='{user}';"):
            return "Error: Username taken"
        if db_connect(f"SELECT * FROM Users WHERE email='{email}';"):
            return "Error: Email taken"
        
        #Random 16-digit user ID
        userid = randnum()

        while db_connect(f"SELECT * FROM Users WHERE userid='{userid}';"):
            userid = randnum()

        pass_hash = hash_password(userid, password)
        
        #Add user to database
        sql = db_connect(
            f'''INSERT INTO Users (userid,name,password,email,date_created)
            VALUES('{userid}','{user}','{pass_hash}','{email}','{time()}');'''
        )
        if sql:
            return sql[0]

        sql = db_connect(
            f'''CREATE TABLE IF NOT EXISTS Contacts{userid} (
                id INTEGER PRIMARY KEY,
                contact TEXT NOT NULL,
                room TEXT,
                date_created DATE,
                status TEXT
            );'''
        )
        if sql:
            return sql[0]

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
            
            if db_connect(f'''SELECT * FROM Users 
                    WHERE userid='{userid}' AND name='{new}';'''):
                return "Error: No changes made"
            
            if user_exists(new):
                return "Error: Username taken"

            sql = db_connect(f'''UPDATE Users SET name='{new}', 
                        password='{hash_password(userid, pw)}'
                        WHERE userid='{userid}';''')
            if sql:
                return sql[0]

        elif mode == "password":
            new = hash_password(userid,new_raw)

            if db_connect(f"SELECT * FROM Users WHERE password='{new}';"):
                return "Error: No changes made"
            
            sql = db_connect(f"UPDATE Users SET password='{new}' WHERE userid='{userid}';")
            if sql:
                return sql[0]

        elif mode == "email":
            new = hashing(new_raw)

            if db_connect(f"SELECT * FROM Users WHERE email='{new}';"):
                return "Error: No changes made"
            if user_exists(new,"email"):
                return "Error: Email taken"
            
            sql = db_connect(f"UPDATE Users SET email='{new}' WHERE userid='{userid}';")
            if sql:
                return sql[0]

        else:
            return "Error: Invalid type of data"

        return "OK"
    
    elif cmd == "add_contact":
        if not validate(get):
            return "Error: Invalid credentials"
        
        user = get[1] #ID of caller user
        other_user = get[3] #Name of second user

        other_id = user_exists(other_user)
        if not other_id:
            return "Error: User not found"
        
        if user == other_id:
            return "Error: Cannot add yourself"

        chat_path = get_directory(other_id,user)

        if table_exists(chat_path):
            return("Error: User already in contacts")

        date_created = time()
        
        sql = create_chat_table(chat_path)
        if sql:
            return sql[0]

        #Add users to list
        sql = db_connect(
            f'''INSERT INTO Contacts{user} (contact,room,date_created)
                VALUES('{other_id}',"{chat_path}",'{date_created}');'''
        )
        if sql:
            return sql[0]

        sql = db_connect(
            f'''INSERT INTO Contacts{other_id} (contact,room,date_created)
                VALUES('{user}',"{chat_path}",'{date_created}');'''
        )
        if sql:
            return sql[0]

        return "Contact added"
    
    elif cmd == "contacts":
        if not validate(get):
            return "Error: Invalid credentials"
        
        user = get[1]

        i = 1
        text = ""

        while True:
            contact = db_connect(f'''SELECT contact FROM Contacts{user} 
                WHERE id={i};''')
            if contact:
                text += contact[0] + "\n"
            else:
                break
            i += 1

        return text.strip()
    
    elif cmd == "version":
        return version

    return "Error: Invalid function " + str(cmd)


#Initialization

#Create user data
db_connect(
    '''CREATE TABLE IF NOT EXISTS Users (
        id INTEGER PRIMARY KEY,
        userid TEXT NOT NULL,
        name TEXT NOT NULL,
        password TEXT NOT NULL,
        email TEXT,
        date_created DATE,
        status TEXT
    );'''
)
create_chat_table("main")

#Get data count
print(db_connect("SELECT count(*) from Users")[0],
    "Users loaded")

print(post_count(), "posts found")

#Create networking socket
print("Starting up server. Press Ctrl+C to close")

async def handle(websocket):
    async for message in websocket:
        with sqlite3.connect(dir_db) as conn:
            get = message.split("\n")
            print("\nConnected",time(),get)
            try:
                resp = str(commands(get)).strip()
            except Exception as e:
                print(traceback.format_exc())
                resp = "Server error: " + str(e)
            print("Response",resp)
            conn.commit()
            await websocket.send(resp)

async def main():
    async with serve(handle, HOST, PORT):
        print("WebSocket created, waiting for connections")
        await asyncio.get_running_loop().create_future()  # run forever

asyncio.run(main())