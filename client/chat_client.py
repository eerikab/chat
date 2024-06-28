import tkinter as tk
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
        self.win = tk.Toplevel(master.win)
        self.win.title("Chat")

        self.font = directory+"/fonts/Cantarell.ttf"
        self.font_bold = directory+"/fonts/Cantarell-Bold.ttf"

        self.master = master
        cw.theme_init(self)

        self.name = user
        self.userid = str(userid)
        self.password = password

        self.page = tk.StringVar(self.win, "Messages")
        self.friend = tk.StringVar(self.win, "main")

        #Create widgets
        self.left = cw.frame(self,self.win,side="left",fill="y")
        self.right = cw.frame(self,self.win,side="right",fill="both",expand=1)

        self.titlebar = cw.frame(self,self.right,fill="x")

        self.page_title = cw.label(self,self.titlebar,text="Page",side="left",padx=8)
        self.search = cw.entry(self,self.titlebar,width=25,side="right",pady=8,padx=8)
        cw.label(self,self.titlebar,text="Search:",side="right")

        self.page_frame = cw.frame(self,self.right,expand=1,fill="both")

        self.title = cw.label(self,self.left, text="Chat",pady=8)
        cw.frame(self,self.left,pady=16)
        cw.radio(self,self.left, 
                text="Posts", 
                value="Posts", 
                variable=self.page,
                padiy=4,
                width=16,
                command=self.switch
                )
        cw.radio(self,self.left, 
                text="Messages", 
                value="Messages", 
                variable=self.page,
                padiy=4,
                width=16,
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
        self.name_label = cw.label(self,self.left, text="Logged in as\n"+self.name,width=15,side="bottom",pady=8)

        self.page_message()
        self.page_post()
        self.contact_strip()

        self.msgs = dict()
        self.msg_min = -1
        self.msg_max = -1
        self.post_min = -1
        self.post_max = -1
        self.users = dict()
        self.posts = dict()
        self.post_btn = []

        self.win.geometry("800x600")
        self.win.minsize(480,360)
        self.win.protocol('WM_DELETE_WINDOW', self.on_exit)

        self.settings = chat_settings.settings()
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
                                      command=self.label.yview,
                                      side="right",
                                      fill="y")

        self.label.config(yscrollcommand=self.scrollbar.set)

        self.frame = cw.frame(self,self.msg_frame,fill="x",side="bottom")
        self.error = cw.label(self,self.frame)
        self.msg_field = cw.text(self,self.frame,
                                 height=3,
                                 fill="x",
                                 padx=16,
                                 expand=1,
                                 )
        cw.button(self,self.frame,
                text="Send message",
                command=self.post,
                pady=8)
        
    def page_post(self):
        self.post_frame = cw.frame(self,self.page_frame)
        self.post_frame.pack_forget()
        self.canvas_frame = cw.frame(self,self.post_frame,fill="both",expand=1)

        self.canvas = cw.canvas(self,self.canvas_frame,fill="both",expand=1,side="left")
        self.post_scrollbar = cw.scroll(self,self.canvas_frame,
                                      command=self.canvas.yview,
                                      side="right",
                                      fill="y")

        self.canvas.configure(yscrollcommand=self.post_scrollbar.set)
        self.posts_frame = cw.frame(self,self.canvas,fill="both",expand=1)
        self.canvas.bind("<Configure>", lambda e: self.canvas.configure(scrollregion = self.posts_frame.bbox()))


        self.canvas.create_window(0,0,window=self.posts_frame,anchor="nw")

        self.frame_post = cw.frame(self,self.post_frame,fill="x",side="bottom")
        self.error_post = cw.label(self,self.frame_post)
        self.post_field = cw.text(self,self.frame_post,
                                 height=3,
                                 fill="x",
                                 padx=16,
                                 expand=1,
                                 )
        cw.button(self,self.frame_post,
                text="Create post",
                command=self.createpost,
                pady=8)
        
    def contact_strip(self):
        self.contacts = cw.frame(self,self.page_frame,side="left")
        self.contacts.pack_forget()
        print("frame")
        cw.label(self,self.contacts,text="Message list",pady=5)
        print("label")
        cw.radio(self,self.contacts,padiy=4,variable=self.friend,text="main",value="main",width=16,command=self.switch)

    def request(self,cmd="",txt=""):
        msg = cmd + "\n" + self.userid + "\n" + self.password + "\n" + txt
        msg = msg.strip()
        ch, resp = self.settings.request(msg)

        if not ch:
            self.error["text"] = resp
            
        return resp

    def post(self):
        _msg = self.msg_field.get(1.0,"end").strip()
        if _msg != "":
            self.request("message",self.chatname+"\n"+_msg)
            self.msg_field.delete(1.0,tk.END)
            self.receive()
    
    def createpost(self):
        _msg = self.post_field.get(1.0,"end").strip()
        if _msg != "":
            self.request("post",_msg)
            self.post_field.delete(1.0,tk.END)
            self.receive()

    def postrecv(self):
        for i in self.post_btn:
            i.button.destroy()
        self.post_btn = []
        #Get total post count
        count = int(self.request("postnum"))
        print("postrecv")
        msg_max = count-1
        msg_min = count-51
        if msg_min < 0:
            msg_min = 0
        self.chkpost(msg_min,msg_max)

        for i in reversed(range(self.post_min,self.post_max+1)):
            self.post_btn.append( postbtn(i,self))

        self.theming()
        self.canvas.configure(scrollregion = self.canvas.bbox("all"))
        self.win.after(100,self.post_region)
        print("postrecv done")
            
    def chkpost(self,msg_min,msg_max):
        if msg_max >= 0:
            for i in range(msg_min,msg_max+1):
                get = self.request("get","post"+str(i)+"\nmsg0")
                get = get.split("\n")
                print(get)
                msg = ""
                for j in get[2:]:
                    msg += j+"\n"
                msg = msg.strip()
                md = {
                        "user" : get[0],
                        "date" : get[1],
                        "msg" : msg
                    }
                self.posts[str(i)] = md

                user = md["user"]
                if not user in self.users:
                    self.users[user] = self.request("user",user)

                if i > self.post_max:
                    self.post_max = i
                if i < self.post_min or self.post_min == -1:
                    self.post_min = i

    def post_region(self):
        self.canvas.configure(scrollregion = self.canvas.bbox("all"))

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
        self.label.delete(1.0,tk.END)
        for i in range(msg_min,msg_max+1):
            msg = self.msgs[str(i)]

            self.label.insert(tk.END,"\n"+self.users[msg["user"]]+" ","User")
            self.label.insert(tk.END,msg["date"][:16]+"\n","Date")
            self.label.insert(tk.END,msg["msg"]+"\n")
        
        self.label.see(tk.END)

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
                    print(get)
                    msg = ""
                    for j in get[2:]:
                        msg += j+"\n"
                    msg = msg.strip()
                    md = {
                        "user" : get[0],
                        "date" : get[1],
                        "msg" : msg
                    }
                    self.msgs[sect] = md

                    user = md["user"]
                    if not user in self.users:
                        self.users[user] = self.request("user",user)

                    config["msg"+sect] = md
                if i > self.msg_max:
                    self.msg_max = i
                if i < self.msg_min or self.msg_min == -1:
                    self.msg_min = i

                i -= 1

            config.write(file)

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
                print(lines)
                self.theme = lines[2].strip()
                self.accent = lines[3].strip()
                self.apply_theme = int(lines[4].strip())
        except:
            self.theme = ""
            self.accent = ""
            self.apply_theme = 1
        
        print("theming",self.theme,self.accent)

        if self.apply_theme:
            #Get theme colours
            theme, accent = cw.theming(self,self.theme,self.accent)
            #print("Theming",self.theme_var.get(),self.accent_var.get())
            col_bg = theme["bg"]
            col_textbox = theme["textbox"]
            col_msg = theme["msg"]
            col_side = theme["side"]
            col_text = theme["text"]
            col_high = theme["high"]
            col_comment = theme["comment"]

            col_button = accent["button"]
            col_user = accent["user"]
            col_button_high = accent["button_high"]
            col_select = accent["selected"]

            #Update widgets with other colours
            self.error["fg"] = "red"
            self.label.tag_configure("User",foreground=col_user,font=self.font+" 10 bold")
            self.label.tag_configure("Date",foreground=col_comment)
            self.left["bg"] = col_side
            self.label["bg"] = col_textbox
            self.name_label["bg"] = col_side
            self.msg_field["bg"] = col_msg
            self.post_field["bg"] = col_msg
            self.title["bg"] = col_side
            self.posts_frame["bg"] = col_textbox
            self.page_title.config(font = self.font + " 10 bold", fg = col_select)

            for i in self.post_btn:
                i.button["bg"] = col_textbox

    def switch(self):
        page = self.page.get()
        self.page_title["text"] = page

        if page == "Posts":
            self.post_frame.pack(fill="both",expand=1,side="right")
            self.msg_frame.pack_forget()
            self.contacts.pack_forget()
            self.postrecv()
        elif page == "Messages":
            self.contacts.pack(fill="y",side="left")
            self.msg_frame.pack(fill="both",expand=1,side="right")
            self.post_frame.pack_forget()
            self.chatname = "main"
            self.receive()
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

class postbtn():
    def __init__(self,i,master=client) -> None:
        text = master.users[master.posts[str(i)]["user"]] + " " + master.posts[str(i)]["date"] + "\n"
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
                width=75,
                justify="left",
                anchor="nw"
            )
        self.i = i
        self.master = master

    def click(self):
        self.master.chatname = "post"+str(self.i)
        self.master.page.set("Post - " + self.master.chatname)
        self.master.switch()
        

def main(user,master,password,userid):
    client(user,master,password,userid)

if __name__ == "__main__": print("Please run the program through chat_main.py")