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
import smtplib
from email.message import EmailMessage

'''Version'''
version = "0.1.2" #Version of server program, increase it with each update
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

smtp_address, smtp_port = "smtp.gmail.com", 587 #Email provider

'''Add data for connecting to PostgreSQL database 
in CHAT_DATABASE environment variable as one string.
For local testing, set up a postgres database in your device 
and add it to CHAT_DATABASE_TEST.

To always use Release data on your server, set CHAT_RELEASE to anything positive.

Set the support email address to CHAT_EMAIL and necessary
credentials for it in CHAT_EMAIL_PASSWORD.

Ideally, set them as environment variables in the server service provider.
Otherwise they are read from env.json in this directory.

Example JSON:
{
"CHAT_DATABASE": "postgresql://postgres.____:____@____.pooler.supabase.com:____/postgres",
"CHAT_DATABASE_TEST": "dbname=chat_server user=postgres password=postgres",s
"CHAT_EMAIL": "example@gmail.com",
"CHAT_EMAIL_PASSWORD": "password123"
}
'''

'''For local testing, you may want to set up Postgres locally
https://docs.fedoraproject.org/en-US/quick-docs/postgresql/

To use a Gmail account to send support mails, make sure to enable
2-factor authentication and set an app password'''

chat_database = ""
chat_database_test = ""
chat_release = 0

support_email = ""
email_pass = ""

ping_interval = 12 * 60 #Message itself every 12 minutes to prevent standby
recovery_time = 20

#Read variables from "env.json" if exists
try:
    with open(os.path.dirname(__file__) + "/env.json") as file:
        data = json.loads(file.read())
        try: chat_database = data["CHAT_DATABASE"]
        except: pass

        try: chat_database_test = data["CHAT_DATABASE_TEST"]
        except: pass

        try: chat_release = data["CHAT_RELEASE"]
        except: pass

        try: support_email = data["CHAT_EMAIL"]
        except: pass
            
        try: email_pass = data["CHAT_EMAIL_PASSWORD"]
        except: pass
except:
    pass

#Load environment variables if exists
if "CHAT_DATABASE" in os.environ:
    chat_database = os.environ["CHAT_DATABASE"]
if "CHAT_DATABASE_TEST" in os.environ:
    chat_database_test = os.environ["CHAT_DATABASE_TEST"]
if "CHAT_RELEASE" in os.environ:
    chat_release = os.environ["CHAT_RELEASE"]

if "CHAT_EMAIL" in os.environ:
    support_email = os.environ["CHAT_EMAIL"]
if "CHAT_EMAIL_PASSWORD" in os.environ:
    email_pass = os.environ["CHAT_EMAIL_PASSWORD"]

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
open_connections = dict()
recoveries = dict()

#Functions
def time_raw():
    '''Return current time in datetime format'''
    return datetime.datetime.now(datetime.timezone.utc)

def time():
    '''Return current time in UTC'''
    return str(time_raw())[:22]

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
    '''Verify user identity through userid and hashed password
    Return empty string upon succeeding or the error message'''
    try:
        #Functions that don't need prior validations
        free_commands = ["login", "register", "version", "email", "reset"]
        if get[0] in free_commands:
            return ""
        
        #Check for username and password
        user = get[1]
        password = get[2]
        session = get[3]
        
        row = db_connect("SELECT password FROM USERS WHERE userid=%s;", (user,))
        if row[0][0] != hash_password(user,password):
            return "Invalid name or password"
        
        #Check for a valid session ID
        if session in open_connections and open_connections[session][1] == user:
            update_connection(session)
            return ""
        else:
            return "Invalid session"

    except Exception as e:
        return "Missing credentials " + str(e)
    
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

def close_connections():
    '''Remove old connections to clients'''
    for i in open_connections.copy():
        if get_time_gap(open_connections[i][2]) > 20 * 60:
            del open_connections[i]

def close_recovery():
    '''Remove expired password reset requests'''
    for i in recoveries.copy():
        if get_time_gap(recoveries[i][0]) > recovery_time * 60:
            del recoveries[i]


def update_connection(sessionid):
    '''Update last ping time for user in connection'''
    for i in open_connections:
        if open_connections[i] == sessionid:
            open_connections[i][2] = time_raw()

def create_session(userid):
    '''Generate session ID for login and add to connections'''
    session = randnum()
    open_connections[session] = [0, userid, time_raw()]
    return session

def update_posts():
    '''Refresh blank entries in posts list
    Temporary solution'''
    ls = db_connect('''SELECT * FROM Posts;''')

    for i in ls:
        #If post data is missing
        if i[2] == None:
            ls = db_connect(
                #Get post data
                psycopg2.sql.SQL('''SELECT * FROM {}''').format(
                    psycopg2.sql.Identifier("post"+str(i[0]))))
            
            #Get first 3 lines of the message
            msg_list = ls[0][3].split("\n")
            msg_short = ""
            for j in msg_list[:3]:
                msg_short += j + "\n"
            
            #Update entry in post list
            sql = db_connect('''UPDATE Posts SET username=%s, date_created=%s, msg=%s, length=%s
                             WHERE id=%s''', (ls[0][1], ls[0][2], msg_short, len(ls), i[0]))
            
def get_time_gap(time=time_raw()):
    '''Return the difference between two datetimes'''
    gap = time_raw() - time
    return gap.total_seconds()
                    

# RESPONSES

def commands(get):
    cmd = get[0]

    verif = validate(get)
    if verif:
        return "Error: " + verif

    if cmd == "message":
        user = get[1]
        msg = ""
        date = time()
        
        post = get_directory(get[4],get[1])
        
        for i in get[5:]:
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
        
        for i in get[4:]:
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
        for i in get[4:7]:
            msg_short += i + "\n"
        
        sql = db_connect('''INSERT INTO Posts(room, username, date_created, msg, length) 
                            VALUES(%s,%s,%s,%s,1);''', (table, user, date, msg_short))
        if sql:
            return sql[0][0]
        
        return "OK"

    elif cmd == "num":
        post = get_directory(get[4],get[1])

        if not check_in_room(post,get[1]):
            return "Error: No access to room"
        
        return db_connect(psycopg2.sql.SQL("SELECT COUNT(*) FROM {};").format(
                psycopg2.sql.Identifier(post)))[0][0]
    
    elif cmd == "postnum":
        return str(post_count())

    elif cmd == "get":
        post = get_directory(get[4],get[1])

        if not check_in_room(post,get[1]):
            return "Error: No access to room"

        ls = db_connect(
                psycopg2.sql.SQL('''SELECT * FROM {} WHERE id>=%s AND id<=%s;''').format(
                    psycopg2.sql.Identifier(post)), (int(get[5]), int(get[6])))
        
        return json.dumps(ls, default=str)
        
        '''msg = ""
        for i in ls:
            msg += "[num]" + str(i[0]) + "\n"
            msg += "[usr]" + i[1] + "\n"
            msg += "[dat]" + str(i[2]) + "\n"
            msg += "[msg]" + i[3] + "\n"
        
        return msg'''

    elif cmd == "getposts":
        #post = get_directory(get[4], get[1])

        ls = db_connect('''SELECT * FROM Posts WHERE id>=%s AND id<=%s;''', (int(get[4]), int(get[5])))
        
        return json.dumps(ls, default=str)
    
    elif cmd == "user":
        user = db_connect("SELECT username FROM Users WHERE userid=%s;", 
                            (get[4],))
        if user:
            return user[0][0]
        else:
            return "[user " + get[4] + "]"

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
            ):
                sessionid = create_session(userid[0][0])
                return userid[0][0] + "\n" + sessionid
        
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
        
        sessionid = create_session(userid)

        return userid + "\n" + sessionid
    
    elif cmd == "update":
        userid = get[1]
        mode = get[4]
        new_raw = get[5]

        #Error checking
        if mode == "username":
            pw = get[6]
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
        
        user = get[1] #ID of caller user
        other_user = get[4] #Name of second user

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
    
    elif cmd == "ping":
        update_connection(get[3])
        return "OK"
    
    elif cmd == "email":
        email = get[1]
        
        data = db_connect('''SELECT userid, username FROM Users WHERE email=%s''', (hashing(hashing(email)),))
        if not data:
            return "Error: Invalid email"
        elif not data[0][0].isnumeric():
            return data[0][0]
        else:
            userid = data[0][0]
            user = data[0][1]
            recovery_code = randnum()[:8]
            while recovery_code in recoveries:
                recovery_code = randnum()
            recoveries[recovery_code] = [time_raw(), email]

            #Send email
            s = smtplib.SMTP(smtp_address, smtp_port)
            s.starttls()

            s.login(support_email, email_pass)
            msg = EmailMessage()
            msg["Subject"] = "Recover your TickChat account"
            msg["From"] = support_email
            msg["To"] = email
            message = f'''Greetings!

A recovery for a TickChat account linked to this email was requested.
Username: {user}

Your one-time recovery code: {recovery_code}
This lasts for {recovery_time} minutes, copy it to the currently open chat window to reset your password.

If you didn't request this message, you can ignore it.
This message was automatically generated, but can be replied to.

Sincerely,
Eerik'''
            if not release:
                message += "\n\nP.S. Server is running on testing mode"
            msg.set_content(message)
            
            s.send_message(msg, support_email, email)
            s.quit()
            return user

    elif cmd == "reset":
        recovery_code = get[1]
        email = get[2]
        password = get[3]

        close_recovery()

        if recovery_code in recoveries and email == recoveries[recovery_code][1]:
            rec = recoveries[recovery_code]

            if email == rec[1] and get_time_gap(rec[0]) < recovery_time * 60:
                userid = db_connect('''SELECT userid, username FROM Users 
                                    WHERE email=%s''', (hashing(hashing(email)),))[0][0]
                new = hash_password(userid, password)

                if db_connect("SELECT * FROM Users WHERE password=%s;", (new,)):
                    return "Error: No changes made"
                
                sql = db_connect('''UPDATE Users SET password=%s 
                                    WHERE userid=%s;''', (new, userid))
                
                if sql:
                    return sql[0][0]
                
                sessionid = create_session(userid)
                return userid + "\n" + sessionid
            
        return "Error: Invalid recovery code"
    

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

update_posts()

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
        #print("Health check failed: ",e)
        pass

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
        close_connections()
        if get[0] == "broadcast":
            open_connections[get[3]][0] = websocket
        #If message posted, broadcast to everyone
        if get[0] == "message":
            conn_list = []
            for i in open_connections:
                if open_connections[i][0]:
                    conn_list.append(open_connections[i][0])
            broadcast(conn_list, resp)

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