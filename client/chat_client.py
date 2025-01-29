'''Background logic behind the main window for chatting rooms and messages'''

import chat_settings as settings
import os
import configparser
import chat_global as cg
import chat_client_gui as ccg

delay = 2000
run = 1
directory = os.path.dirname(__file__)
save = directory+"/chat_settings.txt"
cachedir = directory+"/cache/"

class client():
    def __init__(self,master) -> None:
        #Initialise variables
        self.master = master

        self.chatname = "main"
        self.keep_updating = False
        self.checking = False

        self.msgs = dict()
        self.post_min = -1
        self.post_max = -1
        self.users = dict()
        self.users["main"] = "Main"
        self.posts = dict()
        self.post_btn = []
        self.contact_list = []
        
        self.check_min = 0
        self.check_max = 0

        # Window
        self.gui = ccg.client(self)
        self.win = self.gui.win
        self.get_contacts()
        self.win.widget.after(delay,self.update)
        self.gui.switch()

        '''#Load cache
        os.makedirs(directory+"/cache",exist_ok=True)
        try:
            config = configparser.ConfigParser()
            config.read(cachedir+"main.txt")

            i = 0
            while True:
                sect = "msg"+str(i)
                if config.has_section(sect):
                    msg = dict(config.items(sect))
                    self.msgs[str(i)] = msg
                    i += 1
                    print("Loaded cache",sect)

                    user = msg["user"]
                    if not user in self.users:
                        self.users[user] = self.request("user",user)

                else:
                    break

        except:
            pass'''

    def request(self,cmd="",txt=""):
        msg = cmd + "\n" + cg.userid + "\n" + cg.password + "\n" + txt
        msg = msg.strip()
        ch, resp = settings.request(msg)

        if not ch:
            self.gui.error_current.set(resp)
            
        return resp

    def post(self):
        self.gui.error_current.set("")
        send = self.gui.msg_field.get().strip()
        if send != "":
            if self.request("message",self.chatname+"\n"+send) == "OK":
                self.gui.msg_field.erase()
                self.receive()
    
    def createpost(self):
        self.gui.error_current.set("")
        send = self.gui.post_field.get().strip()
        if send != "":
            if self.request("post",send) == "OK":
                self.gui.post_field.erase()
                self.postrecv()

    def postrecv(self):
        if self.checking:
            return
        self.checking = True
        
        #Get total post count
        try:
            count = int(self.request("postnum"))
        except:
            self.checking = False
            return
        
        for i in self.post_btn:
            i.widget.destroy()
        self.post_btn = []

        msg_max = count
        msg_min = count-50
        if msg_min < 1:
            msg_min = 1
        self.chkpost(msg_min,msg_max)

        for i in reversed(range(self.post_min,self.post_max+1)):
            self.post_btn.append( ccg.postbtn(i,self))

        if not self.post_btn:
            self.post_btn.append( self.gui.post_label("No posts have been made yet"))
        elif msg_min == 1:
            self.post_btn.append( self.gui.post_label("End of the post list"))

        self.win.widget.after(100,self.gui.posts_frame.post_region)
        self.checking = False
            
    def chkpost(self,msg_min,msg_max):
        if msg_max >= 0:
            for i in range(msg_min,msg_max+1):
                length = int(self.request("num","post"+str(i)))
                get = self.request("get","post"+str(i)+"\n1")
                get = get.split("\n")
                msg = ""
                for j in get[2:]:
                    msg += j+"\n"
                msg = msg.strip()
                user = self.get_username(get[0])
                date = settings.time_format(get[1])
                md = {
                        "user" : user,
                        "date" : date,
                        "msg" : msg,
                        "length" : length
                    }
                self.posts[str(i)] = md

                if i > self.post_max:
                    self.post_max = i
                if i < self.post_min or self.post_min == -1:
                    self.post_min = i

    def receive(self):
        if self.checking:
            return
        self.checking = True
        
        try:
            count = int(self.request("num",self.chatname))
        except Exception as e:
            print(e)
            self.checking = False
            return
        
        if self.chatname not in self.msgs:
            self.msgs[self.chatname] = dict()
        if "max" not in self.msgs[self.chatname]:
            self.msgs[self.chatname]["max"] = -1
        if "min" not in self.msgs[self.chatname]:
            self.msgs[self.chatname]["min"] = -1

        self.keep_updating = True
        
        if count != self.msgs[self.chatname]["max"] and count > 0:
            #Get up to 50 messages at a time
            self.gui.label.insert("Loading messages\n","Date")
            msg_max = count
            msg_min = count-50
            if msg_min < 1:
                msg_min = 1
            self.chkmsg(msg_min,msg_max)

        elif self.gui.scrollbar.widget.get()[0] == 0 and self.msgs[self.chatname]["min"] > 1 and not self.just_opened:
            msg_max = self.msgs[self.chatname]["min"]-1
            msg_min = msg_max-51
            if msg_min < 1:
                msg_min = 1
            self.chkmsg(msg_min,msg_max)

        elif not self.just_opened:
            self.checking = False
            return
        self.just_opened = False

        self.gui.label.erase()
        if self.msgs[self.chatname]["max"] < 1:
            self.gui.label.insert("No messages have been sent here yet\n","Date")
            self.gui.label.disable()
            return
        elif self.msgs[self.chatname]["min"] == 1:
            self.gui.label.insert("This is the start of the chat room\n","Date")
        for i in range(self.msgs[self.chatname]["min"], self.msgs[self.chatname]["max"]+1):
            msg = self.msgs[self.chatname][str(i)]
            self.gui.label.insert_msg("\n"+msg["user"], msg["date"], msg["msg"]+"\n")
        self.gui.label.disable()

        self.checking = False

    def chkmsg(self,msg_min,msg_max):
        with open(cachedir+"main.txt","a") as file:
            config = configparser.ConfigParser()
            i = msg_max
            while i >= msg_min:
                sect = str(i)
                try:
                    msg = self.msgs[self.chatname][sect]
                except Exception as e:
                    print(str(e))
                    get = self.request("get",self.chatname +  "\n" + str(i))
                    get = get.split("\n")
                    msg = ""
                    for j in get[2:]:
                        msg += j+"\n"
                    msg = msg.strip()
                    user = self.get_username(get[0])
                    date = settings.time_format(get[1])
                    md = {
                        "user" : user,
                        "date" : date,
                        "msg" : msg
                    }
                    self.msgs[self.chatname][sect] = md

                    #config["msg"+sect] = md
                if not "max" in self.msgs[self.chatname] or i > self.msgs[self.chatname]["max"]:
                    self.msgs[self.chatname]["max"] = i
                if not "min" in self.msgs[self.chatname] or self.msgs[self.chatname]["min"] == -1 or i < self.msgs[self.chatname]["min"]:
                    self.msgs[self.chatname]["min"] = i

                i -= 1

            #config.write(file)

    def update(self):
        if self.keep_updating and not self.checking:
            self.receive()
        self.win.widget.after(delay,self.update)

    def get_contacts(self):
        contacts = self.request("contacts")
        if contacts != "":
            ls = contacts.split("\n")
            ls.reverse()
            for i in ls:
                if i.strip():
                    name = self.get_username(i)
                    if name not in self.contact_list and "error:" not in name.lower():
                        ccg.cw.radio(
                            self, self.gui.contacts,
                            padiy = 4,
                            variable = self.gui.friend,
                            text = name,
                            value = i,
                            width = 16,
                            command = self.gui.switch
                        )
                        ccg.contact_btn(i, self)
                        self.contact_list.append(name)
                    if self.gui.contacts_default:
                        self.gui.contacts_default.destroy()
                        self.gui.contacts_default = 0
            self.win.widget.after(100, self.gui.frame_contacts.post_region)

    def get_username(self,user):
        if not user in self.users:
            self.users[user] = self.request("user",user)

        return self.users[user]
    
    def switch(self):
        page = self.gui.page.get()
        self.just_opened = True
        self.keep_updating = False
        self.checking = False

        if page == "Posts":
            self.postrecv()
        elif page == "Messages":
            self.get_contacts()
            if self.gui.friend.get() != "add contacts":
                self.chatname = self.gui.friend.get()
                self.receive()
        else:
            self.receive()
            self.gui.page.set("Posts")

    def post_click(self):
        self.chatname = "post"+str(self.i)
        self.gui.page.set("Post by " + self.posts[str(self.i)]["user"])
        self.gui.switch()

    def logout(self):
        cg.remember = 0
        cg.password = ""
        cg.userid = ""
        cg.user = ""
        settings.save_user()
        self.win.destroy()
        self.master.login()

    def add_friend(self):
        self.gui.add_error.set("")
        if not self.gui.add_name.get():
            self.gui.add_error.set("Please write a user's name first")
            return
        
        resp = self.request("add_contact", self.gui.add_name.get())
        self.get_contacts()

def main(master):
    client(master)

if __name__ == "__main__": print("Please run the program through chat_main.py")