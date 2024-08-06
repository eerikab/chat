import chat_settings
import os
import configparser
import chat_widgets as cw
import chat_settings_gui as csg

'''Main window of client app, chatting rooms and messages'''

delay = 1000
run = 1
directory = os.path.dirname(__file__)
save = directory+"/chat_settings.txt"
cachedir = directory+"/cache/"

class client():

    def __init__(self,user,master,password,userid) -> None:

        #Initialise window
        self.win = cw.window(self,"Chat","800x600",(640,480))

        self.master = master

        self.name = user
        self.userid = str(userid)
        self.password = password

        self.page = cw.stringvar("Messages")
        self.friend = cw.stringvar("main")

        #Create widgets
        self.left = cw.frame(self,self.win,side="left",fill="y",bg="side")
        self.right = cw.frame(self,self.win,side="right",fill="both",expand=1)

        self.titlebar = cw.frame(self,self.right,fill="x")

        self.page_title = cw.label(self,self.titlebar,text="Page",side="left",padx=8,fg="selected",bold=True,pady=8)
        #self.search = cw.entry(self,self.titlebar,side="right",pady=8,padx=8)
        #cw.label(self,self.titlebar,text="Search:",side="right")

        self.page_frame = cw.frame(self,self.right,expand=1,fill="both")

        self.title = cw.label(self,self.left, text="Chat",pady=8)
        cw.label(self,self.left,pady=4)
        cw.radio(self,self.left, 
                text="Posts", 
                value="Posts", 
                variable=self.page,
                padiy=4,
                width=20,
                command=self.switch
                )
        cw.radio(self,self.left, 
                text="Messages", 
                value="Messages", 
                variable=self.page,
                padiy=4,
                width=20,
                command=self.switch
                )
        cw.button(self,self.left, 
                text="Settings",
                command=self.guiset,
                width=8,
                side="bottom",
                padx=16,
                pady=16)
        cw.button(self,self.left, 
                text="Log out",
                command=self.logout,
                width=8,
                side="bottom",
                padx=16)
        self.name_label = cw.label(self,self.left, text="Logged in as\n"+self.name,width=16,side="bottom",pady=8)

        self.page_message()
        self.page_post()
        self.contact_strip()
        self.page_add()

        self.msgs = dict()
        self.msg_min = -1
        self.msg_max = -1
        self.post_min = -1
        self.post_max = -1
        self.users = dict()
        self.users["main"] = "main"
        self.posts = dict()
        self.post_btn = []
        self.contact_list = []

        self.settings = chat_settings.settings()
        
        self.get_contacts()
        self.theming()

        self.check_min = 0
        self.check_max = 0

        self.chatname = "main"

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

        self.switch()
    
    def page_message(self):
        self.msg_frame = cw.frame(self,self.page_frame,side="right")
        self.msg_frame.pack_forget()
        self.text_frame = cw.frame(self,self.msg_frame,fill="both",expand=1)

        self.label = cw.text(self,self.text_frame,
                             height=1,
                             width=1,
                             fill="both",
                             side="left",
                             expand=1,
                             borderwidth=0
                             )

        self.scrollbar = cw.scroll(self,self.text_frame,
                                      command=self.label.widget.yview,
                                      side="right",
                                      fill="y")

        self.label.widget.config(yscrollcommand=self.scrollbar.widget.set)

        self.frame = cw.frame(self,self.msg_frame,fill="x",side="bottom")
        self.error = cw.error(self,self.frame)
        self.msg_field = cw.text(self,self.frame,
                                 height=3,
                                 fill="x",
                                 padx=16,
                                 expand=1,
                                 bg="msg"
                                 )
        cw.button(self,self.frame,
                text="Send message",
                command=self.post,
                pady=8)
        
    def page_post(self):
        self.post_frame = cw.frame(self,self.page_frame)
        self.post_frame.pack_forget()

        self.posts_frame = cw.canvas_window(self,self.post_frame)

        self.frame_post = cw.frame(self,self.post_frame,fill="x",side="bottom")
        self.error_post = cw.error(self,self.frame_post)
        self.post_field = cw.text(self,self.frame_post,
                                 height=3,
                                 fill="x",
                                 padx=16,
                                 expand=1,
                                 bg="msg"
                                 )
        cw.button(self,self.frame_post,
                text="Create post",
                command=self.createpost,
                pady=8)
        
    def contact_strip(self):
        self.contacts = cw.frame(self,self.page_frame,side="left")
        self.contacts.pack_forget()
        cw.radio(self,self.contacts,padiy=4,variable=self.friend,text="Add contacts",value="add contacts",width=16,command=self.switch)
        cw.label(self,self.contacts,text="Message list",pady=4)
        cw.radio(self,self.contacts,padiy=4,variable=self.friend,text="main",value="main",width=16,command=self.switch)

    def page_add(self):
        self.frame_add = cw.frame(self,self.page_frame,side="left")
        self.frame_add.pack_forget()
        cw.label(self,self.frame_add,text="Enter a friend's username to add them to contact list:")
        self.add_name = cw.entry(self,self.frame_add,pady=8)
        cw.button(self,self.frame_add,text="Add",command=self.add_friend)
        self.add_error = cw.label(self,self.frame_add,text="")
        cw.label(self,self.frame_add,text="Direct messages:")
        #self.frame_contacts = cw.frame(self,self.frame_add,expand=1,fill="both",bg="textbox")
        self.frame_contacts = cw.canvas_window(self,self.frame_add)

    def request(self,cmd="",txt=""):
        msg = cmd + "\n" + self.userid + "\n" + self.password + "\n" + txt
        msg = msg.strip()
        ch, resp = self.settings.request(msg)

        if not ch:
            self.error.set(resp)
            
        return resp

    def post(self):
        _msg = self.msg_field.get()
        if _msg != "":
            self.request("message",self.chatname+"\n"+_msg)
            self.msg_field.erase()
            self.receive()
    
    def createpost(self):
        _msg = self.post_field.get()
        if _msg != "":
            self.request("post",_msg)
            self.post_field.erase()
            self.postrecv()

    def postrecv(self):
        for i in self.post_btn:
            i.button.destroy()
        self.post_btn = []
        #Get total post count
        count = int(self.request("postnum"))
        msg_max = count-1
        msg_min = count-51
        if msg_min < 0:
            msg_min = 0
        self.chkpost(msg_min,msg_max)

        for i in reversed(range(self.post_min,self.post_max+1)):
            self.post_btn.append( postbtn(i,self))

        self.theming()
        self.win.widget.after(100,self.posts_frame.post_region)

            
    def chkpost(self,msg_min,msg_max):
        if msg_max >= 0:
            for i in range(msg_min,msg_max+1):
                get = self.request("get","post"+str(i)+"\nmsg0")
                get = get.split("\n")
                msg = ""
                for j in get[2:]:
                    msg += j+"\n"
                msg = msg.strip()
                user = self.get_username(get[0])
                md = {
                        "user" : user,
                        "date" : get[1],
                        "msg" : msg
                    }
                self.posts[str(i)] = md

                if i > self.post_max:
                    self.post_max = i
                if i < self.post_min or self.post_min == -1:
                    self.post_min = i

    def receive(self):
        self.msgs.clear()
        count = int(self.request("num",self.chatname))

        #Get up to 50 messages at a time
        msg_max = count-1
        msg_min = count-51
        if msg_min < 0:
            msg_min = 0
        self.chkmsg(msg_min,msg_max)

        '''if count != self.msg_max+1:
            #Get up to 50 messages at a time
            msg_max = count-1
            msg_min = count-51
            if msg_min < 0:
                msg_min = 0
            self.chkmsg(msg_min,msg_max)

        elif self.scrollbar.get()[0] == 0 and self.msg_min > 0:
            msg_max = self.msg_min-1
            msg_min = msg_max-51
            if msg_min < 0:
                msg_min = 0
            self.chkmsg(msg_min,msg_max)

        else: return'''

        #print(self.msgs)

        num = 0
        self.label.erase()
        for i in range(msg_min,msg_max+1):
            msg = self.msgs[str(i)]

            self.label.insert("\n"+msg["user"]+"     ","User")
            self.label.insert(msg["date"][:16]+"\n","Date")
            self.label.insert(msg["msg"]+"\n")

    def chkmsg(self,msg_min,msg_max):
        with open(cachedir+"main.txt","a") as file:
            config = configparser.ConfigParser()
            i = msg_max
            while i >= msg_min:
                sect = str(i)
                try:
                    msg = self.msgs[sect]
                except Exception as e:
                    #print(str(e))
                    get = self.request("get",self.chatname +  "\nmsg" + str(i))
                    get = get.split("\n")
                    msg = ""
                    for j in get[2:]:
                        msg += j+"\n"
                    msg = msg.strip()
                    user = self.get_username(get[0])
                    md = {
                        "user" : user,
                        "date" : get[1],
                        "msg" : msg
                    }
                    self.msgs[sect] = md

                    config["msg"+sect] = md
                if i > self.msg_max:
                    self.msg_max = i
                if i < self.msg_min or self.msg_min == -1:
                    self.msg_min = i

                i -= 1

            config.write(file)

    def get_contacts(self):
        contacts = self.request("contacts")
        if contacts != "":
            ls = contacts.split("\n")
            ls.reverse()
            for i in ls:
                name = self.get_username(i)
                if name not in self.contact_list:
                    cw.radio(self,self.contacts,padiy=4,variable=self.friend,text=name,value=i,width=16,command=self.switch)
                    contact_btn(i,self)
                    self.contact_list.append(name)
            self.theming()
            self.win.widget.after(100,self.frame_contacts.post_region)

    def get_username(self,user):
        if not user in self.users:
            self.users[user] = self.request("user",user)

        return self.users[user]

    def guiset(self):
        csg.guiset(self,self.win)

    def on_exit(self):
        try:
            self.settings.win.destroy()
        except:
            pass

        self.win.destroy()
        self.master.win.destroy()

    def theming(self):
        #Function used to theme local settings window
        #Update selected theme name
        try:
            with open(save,"r") as file:
                lines = file.readlines()
                self.theme = lines[2].strip()
                self.accent = lines[3].strip()
                self.apply_theme = int(lines[4].strip())
        except:
            self.theme = ""
            self.accent = ""
            self.apply_theme = 1

        if self.apply_theme:
            #Get theme colours
            cw.theming(self,self.theme,self.accent)

    def post_click(self):
        self.chatname = "post"+str(self.i)
        self.page.set("Post by " + self.posts[str(self.i)]["user"])
        self.switch()

    def switch(self):
        page = self.page.get()
        self.page_title.set(page)

        if page == "Posts":
            self.post_frame.pack(fill="both",expand=1,side="right")
            self.msg_frame.pack_forget()
            self.contacts.pack_forget()
            self.frame_add.pack_forget()
            self.postrecv()
        elif page == "Messages":
            self.contacts.pack(fill="y",side="left")
            if self.friend.get() == "add contacts":
                self.frame_add.pack(fill="both",expand=1,side="right")
                self.msg_frame.pack_forget()
                self.add_error.set("")
                self.page_title.set("Messages - Add contacts")
            else:
                self.msg_frame.pack(fill="both",expand=1,side="right")
                self.frame_add.pack_forget()
                self.chatname = self.friend.get()
                self.receive()
                self.page_title.set("Messages - " + self.get_username(self.chatname))
            self.post_frame.pack_forget()
            self.get_contacts()
        else:
            self.msg_frame.pack(fill="both",expand=1,side="right")
            self.post_frame.pack_forget()
            self.receive()

    def logout(self):
        self.win.destroy()
        with open(save,"w") as file:
            file.write("\n")
            file.write("\n"+self.theme)
            file.write("\n"+self.accent)
            file.write("\n"+str(self.apply_theme))
        self.master.login()

    def add_friend(self):
        resp = self.request("add_contact", self.add_name.get() )
        self.add_error.set(resp)
        self.get_contacts()

class postbtn():
    def __init__(self,i,master=client) -> None:
        text = master.posts[str(i)]["user"] + "     " + master.posts[str(i)]["date"] + "\n"
        count = 0
        for line in master.posts[str(i)]["msg"].strip().split("\n"):
            if count < 3:
                text += "\n" + line
            else: 
                break
            count += 1
            

        self.button = cw.button(
                master, master.posts_frame,
                text = text,
                command = self.click,
                fill = "both",
                padx=8,
                pady=8,
                expand=1,
                justify="left",
                anchor="nw",
                bg="textbox"
            )
        self.i = i
        self.master = master

    def click(self):
        self.master.chatname = "post"+str(self.i)
        self.master.page.set("Post by " + self.master.posts[str(self.i)]["user"])
        self.master.switch()

class contact_btn():
    def __init__(self,i,master=client) -> None:
        text = master.get_username(i)

        self.button = cw.button(
                master, master.frame_contacts,
                text = text,
                command = self.click,
                fill = "both",
                padx=8,
                pady=8,
                expand=1,
                justify="left",
                anchor="nw",
                bg="textbox"
            )
        self.i = i
        self.master = master

    def click(self):
        self.master.friend.set(self.i)
        self.master.switch()
        
def main(user,master,password,userid):
    client(user,master,password,userid)

if __name__ == "__main__": print("Please run the program through chat_main.py")