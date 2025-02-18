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
import psycopg2.sql
from websockets.server import serve
from websockets.server import broadcast
from websockets.client import connect
#import sqlite3
import traceback
import psycopg2
import json
import http
import signal

'''Version'''
version = "0.1.0a2" #Version of server program, increase it with each update
py_version = sys.version.split()[0]
print("Server program version", version)
print("Python version", sys.version)

'''Debug/Release switch
When it's 1, public IP and production database is used
On 0, it uses localhost and testing database
Instructions for forcing release database on your server below'''
release = 0

'''For client programs, the switch and IP to connect to is in
client/chat_global.py and web/scripts/functions.js respectively'''

'''IP Addresses'''
HOST, PORT = "0.0.0.0", 9000 #Production IP
HOST_TEST, PORT_TEST = "127.0.0.1", 9000 #Testing IP

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

ping_interval = 12 * 60 #Message itself every 12 minutes to prevent standby

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
    print("Using Release mode")
    host_current, port_current = HOST, PORT
    try:
        db_address = chat_database
    except:
        print("ERROR: Missing connection to database")
        print("Please add it in CHAT_DATABASE environment variable")
        exit()
else:
    print("Using Testing mode")
    host_current, port_current = HOST_TEST, PORT_TEST
    try:
        db_address = chat_database_test
    except:
        print("ERROR: Missing connection to development database")
        print("Please add it in CHAT_DATABASE_TEST environment variable")
        exit()

print("Server:", host_current, port_current)
print("Database:", db_address)

#Data directories
#Deprecated by use of external postgres database
dir_data = os.path.dirname(__file__)+"/data/"
#Why should the folder already existing cause an error by default?
os.makedirs(dir_data, exist_ok=True) 
dir_db = dir_data + "data.db"

#Database connection
class db_connection():
    '''Database connection for psycopg2'''

    def connect(self):
        self.conn = psycopg2.connect(db_address)
        self.cursor = self.conn.cursor()

    def execute(self, statement="", data=()):
        self.cursor.execute(statement, data)
        try:
            return self.cursor.fetchall()
        except:
            return ()
        
    def close(self):
        self.conn.commit()
        self.cursor.close()
        self.conn.close()

db = db_connection()
open_connections = []

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
    
def db_connect(statement="", data=()):
    '''Communicate with SQL database
    Uses PostgreSQL'''
    try:
        return db.execute(statement, data)
            
    except Exception as e:
        print(traceback.format_exc())
        print("Failed to open database: ", e)
        return ("Server error: " + str(e),)

def validate(get):
    '''Verify user identity through userid and hashed password'''
    try:
        user = get[1]
        password = get[2]
        row = db_connect("SELECT password FROM USERS WHERE userid=%s;", (user,))
        if row[0][0] == hash_password(user,password):
            return True
        else:
            return False
    except:
        return False
    
def user_exists(name="",key="username"):
    '''Check if username or email is taken in the database'''
    user = db_connect(psycopg2.sql.SQL('''SELECT userid FROM Users 
                WHERE LOWER({})=%s;''').format(
                    psycopg2.sql.Identifier(key)
                ), (name.lower(),))
    if user:
        return user[0][0]
    else:
        return ""

def get_directory(file="",userid=""):
    '''Find the appropriate table based on chatroom'''
    #Postgres expects lowercase table names
    if file[:4].lower() == "post":
        #Post files start with "post", followed by index
        return "post" + file[4:]
    elif len(file) == 16 and file.isdigit():
        #Direct message names are composed of both user IDs, smaller first
        #Here, userid is caller and file is callee
        if int(file) < int(userid):
            return "room" + file + userid
        else:
            return "room" + userid + file
    else:
        #Misc stuff defaults to the parent directory
        return file

def check_in_room(room_name="",id=""):
    '''Check if user has access to room
    Private message rooms are composed of two 16-digit user IDs'''
    if len(room_name) < 36:
        return True
    elif db_connect(psycopg2.sql.SQL('''SELECT * FROM {}
            WHERE LOWER(room)=%s;''').format(
                psycopg2.sql.Identifier("contacts"+id)), (room_name,)
    ):
        return True
    else:
        return False
    
def table_exists(table):
    '''Check if table exists in database'''
    var = db_connect('''SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_name = %s);''', (table,))[0][0]
    return var == "True"
    
def create_chat_table(room):
    '''Create a chat room in database'''
    #Statements modifying the database should return an empty tuple
    #If a value is returned, something went wrong
    return db_connect(psycopg2.sql.SQL(
        '''CREATE TABLE IF NOT EXISTS {} (
            id SERIAL PRIMARY KEY,
            username VARCHAR(32) NOT NULL,
            date_created TIMESTAMP NOT NULL,
            msg VARCHAR(500) NOT NULL,
            status VARCHAR(10)
        );''').format(psycopg2.sql.Identifier(room.lower()))
    )

def post_count():
    '''Get the amount of posts sent'''
    return db_connect("SELECT COUNT(*) FROM Posts")[0][0]


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
        
        sql = db_connect(psycopg2.sql.SQL('''INSERT INTO {} 
                (username, date_created, msg) VALUES(%s,%s,%s);''').format(
                    psycopg2.sql.Identifier(post.lower())), 
                (user, date, msg))
        if sql:
            return sql[0][0]
        
        length = db_connect(psycopg2.sql.SQL('''SELECT COUNT(*) FROM {};''').format(
                    psycopg2.sql.Identifier(post.lower())))[0][0]
        if "post" in post.lower():
            sql = db_connect('''UPDATE Posts SET length=%s WHERE room=%s;''', (length, post))
            if sql:
                return sql[0][0]

        return f"update\n{post}\n{length}\n{user}\n{date}\n{msg}"

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

        table = "post" + str(post_count() + 1)
        sql = create_chat_table(table)
        if sql:
            return sql[0][0]
        
        sql = db_connect(psycopg2.sql.SQL('''INSERT INTO {} 
                    (username, date_created, msg) VALUES(%s,%s,%s);''').format(
                        psycopg2.sql.Identifier(table)), (user, date, msg))
        if sql:
            return sql[0][0]
        
        msg_short = ""
        for i in get[3:6]:
            msg_short += i + "\n"
        
        sql = db_connect('''INSERT INTO Posts(room, username, date_created, msg, length) 
                            VALUES(%s,%s,%s,%s,1);''', (table, user, date, msg_short))
        if sql:
            return sql[0][0]
        
        return "OK"

    elif cmd == "num":
        if not validate(get):
            return "Error: Invalid credentials"
        
        post = get_directory(get[3],get[1])

        if not check_in_room(post,get[1]):
            return "Error: No access to room"
        
        return db_connect(psycopg2.sql.SQL("SELECT COUNT(*) FROM {};").format(
                psycopg2.sql.Identifier(post)))[0][0]
    
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

        ls = db_connect(
                psycopg2.sql.SQL('''SELECT * FROM {} WHERE id>=%s AND id<=%s;''').format(
                    psycopg2.sql.Identifier(post)), (int(get[4]), int(get[5])))
        
        return json.dumps(ls, default=str)
        
        '''msg = ""
        for i in ls:
            msg += "[num]" + str(i[0]) + "\n"
            msg += "[usr]" + i[1] + "\n"
            msg += "[dat]" + str(i[2]) + "\n"
            msg += "[msg]" + i[3] + "\n"
        
        return msg'''

    elif cmd == "getposts":
        if not validate(get):
            return "Error: Invalid credentials"

        #post = get_directory(get[3], get[1])

        ls = db_connect('''SELECT * FROM Posts WHERE id>=%s AND id<=%s;''', (int(get[3]), int(get[4])))
        
        return json.dumps(ls, default=str)
    
    elif cmd == "user":
        if not validate(get):
            return "Error: Invalid credentials"
        user = db_connect("SELECT username FROM Users WHERE userid=%s;", 
                            (get[3],))
        if user:
            return user[0][0]
        else:
            return "[user " + get[3] + "]"

    elif cmd == "login":
        user = get[1]
        password = get[2]
        userid = db_connect(
            '''SELECT userid FROM Users WHERE username=%s 
                OR email=%s;''', (user, hashing(user))
        )

        if userid:
            if db_connect(
                '''SELECT userid FROM Users
                WHERE (username=%s OR email=%s) AND password=%s;''', 
                (user, hashing(user), hash_password(userid[0][0], password))
            ) or "error" in userid[0][0]:
                return userid[0][0]
        
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
        
        if db_connect("SELECT * FROM Users WHERE username=%s;", (user,)):
            return "Error: Username taken"
        if db_connect("SELECT * FROM Users WHERE email=%s;", (email,)):
            return "Error: Email taken"
        
        #Random 16-digit user ID
        userid = randnum()

        while db_connect("SELECT * FROM Users WHERE userid=%s;", (userid,)):
            userid = randnum()

        pass_hash = hash_password(userid, password)
        
        #Add user to database
        sql = db_connect(
            '''INSERT INTO Users (userid,username,password,email,date_created)
            VALUES(%s,%s,%s,%s,%s);''', (userid, user, pass_hash, email, time())
        )
        if sql:
            return sql[0][0]

        sql = db_connect(
            psycopg2.sql.SQL('''CREATE TABLE IF NOT EXISTS {} (
                id SERIAL PRIMARY KEY,
                contact CHAR(16) NOT NULL,
                room CHAR(36),
                date_created TIMESTAMP,
                status VARCHAR(10)
            );''').format(psycopg2.sql.Identifier("contacts" + userid))
        )
        if sql:
            return sql[0][0]

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
            
            if db_connect('''SELECT * FROM Users 
                    WHERE userid=%s AND username=%s;''', (userid, new)):
                return "Error: No changes made"
            
            if user_exists(new):
                return "Error: Username taken"

            sql = db_connect('''UPDATE Users SET username=%s, password=%s
                    WHERE userid=%s;''', (new, hash_password(userid,pw), userid))
            if sql:
                return sql[0][0]

        elif mode == "password":
            new = hash_password(userid,new_raw)

            if db_connect("SELECT * FROM Users WHERE password=%s;", (new,)):
                return "Error: No changes made"
            
            sql = db_connect('''UPDATE Users SET password=%s 
                                WHERE userid=%s;''', (new, userid))
            if sql:
                return sql[0][0]

        elif mode == "email":
            new = hashing(new_raw)

            if db_connect("SELECT * FROM Users WHERE email=%s;", (new,)):
                return "Error: No changes made"
            if user_exists(new,"email"):
                return "Error: Email taken"
            
            sql = db_connect('''UPDATE Users SET email=%s
                                WHERE userid=%s;''', (new, userid))
            if sql:
                return sql[0][0]

        else:
            return "Error: Invalid type of data"

        return "OK"
    
    elif cmd == "addcontact":
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
            return sql[0][0]

        #Add users to list
        sql = db_connect(
            psycopg2.sql.SQL('''INSERT INTO {} (contact,room,date_created)
                VALUES(%s,%s,%s);''').format(
                    psycopg2.sql.Identifier("contacts"+user)), 
                (other_id, chat_path, date_created)
        )
        if sql:
            return sql[0][0]

        sql = db_connect(
            psycopg2.sql.SQL('''INSERT INTO {} (contact,room,date_created)
                VALUES(%s,%s,%s);''').format(
                    psycopg2.sql.Identifier("contacts"+other_id)), 
                (user, chat_path, date_created)
        )
        if sql:
            return sql[0][0]

        return "Contact added"
    
    elif cmd == "contacts":
        if not validate(get):
            return "Error: Invalid credentials"
        
        user = get[1]
        text = ""

        contact = db_connect( psycopg2.sql.SQL(
            '''SELECT contact FROM {};''').format(
                psycopg2.sql.Identifier("contacts"+user)))
            
        for i in contact:
            text += i[0] + "\n"

        return text.strip()
    
    elif cmd == "version":
        return version
    
    elif cmd == "broadcast":
        return "OK"

    return "Error: Invalid function " + str(cmd)


#Initialization

db.connect()
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
        status VARCHAR(10),
        length INTEGER
    );'''
)

#Length column wasn't there at first
db_connect('''ALTER TABLE Posts ADD COLUMN IF NOT EXISTS length INTEGER;''')

#Get data count
print(db_connect("SELECT count(*) from Users")[0][0], "users loaded")
print(post_count(), "posts found")

db.close()

#Create networking socket
print("Starting up server. Press Ctrl+C to close")

def health_check(connection, request):
    '''Health check for Render cloud'''
    #Very likely fails on local testing unless health check explicitly set
    try:
        if request.path == "/healthz":
            return connection.respond(http.HTTPStatus.OK, "OK\n")
    except Exception as e:
        print("Health check failed: ",e)

async def keepalive():
    '''Create a connection periodically to keep server running'''
    while True:
        await asyncio.sleep(ping_interval)
        try:
            if release:
                async with connect("wss://chat-4zh4.onrender.com",) as socket:
                    print("\nSent periodic ping")
                    await socket.send("version")
                    await socket.recv()
        except:
            try:
                async with connect(f"ws://{host_current}:{port_current}") as socket:
                    print("\nSent periodic ping")
                    await socket.send("version")
                    await socket.recv()
            except Exception as e:
                print("Failed to send keepalive ping: ",e)

async def handle(websocket):
    '''Handle client connections'''
    async for message in websocket:
        get = message.split("\n")
        print("\nConnected",time(),get)
        db.connect() #Open database connection

        try:
            resp = str(commands(get)).strip()
        except Exception as e:
            print(traceback.format_exc())
            resp = "Server error: " + str(e)
        
        db.close()
        print("Response",resp)
        await websocket.send(resp)

        #Add to broadcast list
        if get[0] == "broadcast":
            open_connections.append(websocket)
        #If message posted, broadcast to everyone
        if get[0] == "message":
            broadcast(open_connections, resp)
        print(open_connections)

async def main():
    loop = asyncio.get_running_loop()
    stop = loop.create_future()
    loop.add_signal_handler(signal.SIGTERM, stop.set_result, None)

    async with serve(
        handle, 
        host = host_current, 
        port = port_current, 
        process_request = health_check
    ):
        print("Server started at",time())
        print("WebSocket created, waiting for connections")
        asyncio.create_task(keepalive())
        await stop  # run forever

asyncio.run(main())