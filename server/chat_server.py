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
import psycopg2
import json

'''Debug/Release switch
When it's 1, public IP and production database is used
On 0, it uses localhost and testing database'''
release = 1

'''For client programs, the switch and IP to connect to is in
client/chat_global.py and web/scripts/functions.js respectively'''

'''IP Addresses'''
HOST, PORT = "0.0.0.0", 9000 #Production IP
HOST_TEST, PORT_TEST = "localhost", 9000 #Testing IP

'''Add data for connecting to PostgreSQL database 
in CHAT_DATABASE environment variable as one string.
For local testing, set up a postgres database in your device 
and add it to CHAT_DATABASE_TEST.

To always use Release data on your server, set CHAT_RELEASE to anything positive.

Ideally, set them as environment variables in the server service provider.
Otherwise they are read from env.json in this directory.

Example JSON:
{
"CHAT_DATABASE": "postgresql://postgres.____:____@____.pooler.supabase.com:____/postgres",
"CHAT_DATABASE_TEST": "dbname=chat_server user=postgres password=postgres"
}
'''

chat_database = ""
chat_database_test = ""
chat_release = 0

#Read variables from "env.json" if exists
try:
    with open(os.path.dirname(__file__) + "/env.json") as file:
        data = json.loads(file.read())
        try:
            chat_database = data["CHAT_DATABASE"]
        finally:
            try:
                chat_database_test = data["CHAT_DATABASE_TEST"]
            finally:
                try:
                    chat_release = data["CHAT_RELEASE"]
                except:
                    pass
except:
    pass

#Load environment variables if exists
if "CHAT_DATABASE" in os.environ:
    chat_database = os.environ["CHAT_DATABASE"]
if "CHAT_DATABASE_TEST" in os.environ:
    chat_database_test = os.environ["CHAT_DATABASE_TEST"]
if "CHAT_RELEASE" in os.environ:
    chat_release = os.environ["CHAT_RELEASE"]

if chat_release:
    release = 1

if release:
    host_current, port_current = HOST, PORT
    try:
        db_address = chat_database
    except:
        print("ERROR: Missing connection to database")
        print("Please add it in CHAT_DATABASE environment variable")
        exit()
else:
    host_current, port_current = HOST_TEST, PORT_TEST
    try:
        db_address = chat_database_test
    except:
        print("ERROR: Missing connection to development database")
        print("Please add it in CHAT_DATABASE_TEST environment variable")
        exit()


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
    Uses PostgreSQL'''
    try:
        with psycopg2.connect(db_address) as conn:
            cursor = conn.cursor()
            cursor.execute(statement)
            try:
                return cursor.fetchone()
            except:
                return ()
            
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
    
def user_exists(name="",key="username"):
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
            WHERE room='{room_name}';'''):
        return True
    else:
        return False
    
def table_exists(table):
    '''Check if table exists in database'''
    var = db_connect(f'''SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_name = '{table}');''')
    return var == "True"
    
def create_chat_table(room):
    '''Create a chat room in database'''
    #Statements modifying the database should return an empty tuple
    #If a value is returned, something went wrong
    return db_connect(
        f'''CREATE TABLE IF NOT EXISTS {room} (
            id SERIAL PRIMARY KEY,
            username VARCHAR(32) NOT NULL,
            date_created TIMESTAMP NOT NULL,
            msg VARCHAR(500) NOT NULL,
            status VARCHAR(10)
        );'''
    )

def post_count():
    '''Get the amount of posts sent'''
    return db_connect("SELECT COUNT(*) FROM Posts")[0]


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
        
        sql = db_connect(f'''INSERT INTO {post}(username, date_created, msg)
                   VALUES('{user}','{date}','{msg}');''')
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
        
        sql = db_connect(f'''INSERT INTO {table}(username, date_created, msg)
                   VALUES('{user}','{date}','{msg}');''')
        if sql:
            return sql[0]
        
        sql = db_connect(f'''INSERT INTO Posts(room) VALUES('{table}');''')
        if sql:
            return sql[0]
        
        return "OK"

    elif cmd == "num":
        if not validate(get):
            return "Error: Invalid credentials"
        
        post = get_directory(get[3],get[1])

        if not check_in_room(post,get[1]):
            return "Error: No access to room"
        
        return db_connect(f"SELECT COUNT(*) FROM {post};")[0]
    
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
        msg = ls[1] + "\n" + str(ls[2]) + "\n" + ls[3]
        
        return msg
    
    elif cmd == "user":
        if not validate(get):
            return "Error: Invalid credentials"
        user = db_connect(f"SELECT username FROM Users WHERE userid='{get[3]}';")
        if user:
            return user[0]
        else:
            return "[user " + get[3] + "]"

    elif cmd == "login":
        user = get[1]
        password = get[2]
        userid = db_connect(
            f'''SELECT userid FROM Users
                WHERE username='{user}' OR email='{hashing(user)}';'''
        )

        if userid:
            if db_connect(
                f'''SELECT userid FROM Users
                WHERE (username='{user}' OR email='{hashing(user)}')
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
        
        if db_connect(f"SELECT * FROM Users WHERE username='{user}';"):
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
            f'''INSERT INTO Users (userid,username,password,email,date_created)
            VALUES('{userid}','{user}','{pass_hash}','{email}','{time()}');'''
        )
        if sql:
            return sql[0]

        sql = db_connect(
            f'''CREATE TABLE IF NOT EXISTS Contacts{userid} (
                id SERIAL PRIMARY KEY,
                contact CHAR(16) NOT NULL,
                room CHAR(36),
                date_created TIMESTAMP,
                status VARCHAR(10)
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
                    WHERE userid='{userid}' AND username='{new}';'''):
                return "Error: No changes made"
            
            if user_exists(new):
                return "Error: Username taken"

            sql = db_connect(f'''UPDATE Users SET username='{new}', 
                        password='{hash_password(userid, pw)}'
                        WHERE userid='{userid}';''')
            if sql:
                return sql[0]

        elif mode == "password":
            new = hash_password(userid,new_raw)

            if db_connect(f"SELECT * FROM Users WHERE password='{new}';"):
                return "Error: No changes made"
            
            sql = db_connect(f'''UPDATE Users SET password='{new}' 
                                WHERE userid='{userid}';''')
            if sql:
                return sql[0]

        elif mode == "email":
            new = hashing(new_raw)

            if db_connect(f"SELECT * FROM Users WHERE email='{new}';"):
                return "Error: No changes made"
            if user_exists(new,"email"):
                return "Error: Email taken"
            
            sql = db_connect(f'''UPDATE Users SET email='{new}' 
                                WHERE userid='{userid}';''')
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
                VALUES('{other_id}','{chat_path}','{date_created}');'''
        )
        if sql:
            return sql[0]

        sql = db_connect(
            f'''INSERT INTO Contacts{other_id} (contact,room,date_created)
                VALUES('{user}','{chat_path}','{date_created}');'''
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
#db_connect('''DROP TABLE IF EXISTS Posts''')

db_connect(
    '''CREATE TABLE IF NOT EXISTS Users (
        id SERIAL PRIMARY KEY,
        userid CHAR(16) NOT NULL,
        username VARCHAR(32) NOT NULL,
        password CHAR(64) NOT NULL,
        email CHAR(64),
        date_created TIMESTAMP,
        status VARCHAR(10)
    );'''
)

create_chat_table("main")

db_connect(
    '''CREATE TABLE IF NOT EXISTS Posts (
        id SERIAL PRIMARY KEY,
        room CHAR(36),
        username VARCHAR(32),
        date_created TIMESTAMP,
        msg VARCHAR(500),
        status VARCHAR(10)
    );'''
)

#Get data count
print(db_connect("SELECT count(*) from Users")[0],
    "Users loaded")

print(post_count(), "posts found")

#Create networking socket
print("Starting up server. Press Ctrl+C to close")

async def handle(websocket):
    async for message in websocket:
        get = message.split("\n")
        print("\nConnected",time(),get)
        try:
            resp = str(commands(get)).strip()
        except Exception as e:
            print(traceback.format_exc())
            resp = "Server error: " + str(e)
        print("Response",resp)
        await websocket.send(resp)

async def main():
    async with serve(handle, host_current, port_current):
        print("WebSocket created, waiting for connections")
        await asyncio.get_running_loop().create_future()  # run forever

asyncio.run(main())