'''Graphical interface for the main window for chatting rooms and messages'''

import chat_settings as settings
import chat_widgets as cw
import chat_settings_gui as csg
import chat_global as cg

class client():
    def __init__(self,master) -> None:

        #Initialise window
        self.win = cw.window(self,"Chat","800x600",(640,480))
        self.master = master

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

        self.title = cw.label(self,self.left, text="Chat",pady=8,bold=True,fg="selected")
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
                command=self.master.logout,
                width=8,
                side="bottom",
                padx=16)
        self.name_label = cw.label(
                self, self.left, 
                text="Logged in as\n" + cg.user, 
                width=16, 
                side="bottom", 
                pady=8
        )

        self.page_message()
        self.page_post()
        self.contact_strip()
        self.page_add()
    
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
        self.label.disable()

        self.scrollbar = cw.scroll(self,self.text_frame,
                                      command=self.label.widget.yview,
                                      side="right",
                                      fill="y")

        self.label.widget.config(yscrollcommand=self.scrollbar.widget.set)

        self.frame = cw.frame(self,self.msg_frame,fill="x",side="bottom")
        self.error = cw.error(self,self.frame)
        self.error_current = self.error
        self.msg_field = cw.text(self,self.frame,
                                 height=3,
                                 fill="x",
                                 padx=16,
                                 expand=1,
                                 bg="msg"
                                 )
        cw.button(self,self.frame,
                text="Send message",
                command=self.master.post,
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
                command=self.master.createpost,
                pady=8)
        
    def contact_strip(self):
        self.contacts = cw.frame(self,self.page_frame,side="left")
        self.contacts.pack_forget()
        cw.radio(self,self.contacts,padiy=4,variable=self.friend,text="Add contacts",value="add contacts",width=16,command=self.switch)
        cw.label(self,self.contacts,text="Message list",pady=4)
        cw.radio(self,self.contacts,padiy=4,variable=self.friend,text="Main",value="main",width=16,command=self.switch)

    def page_add(self):
        self.frame_add = cw.frame(self,self.page_frame,side="left")
        self.frame_add.pack_forget()
        cw.label(self,self.frame_add,text="Enter a friend's username to add them to contact list:")
        self.add_name = cw.entry(self,self.frame_add,pady=8)
        cw.button(self,self.frame_add,text="Add",command=self.master.add_friend)
        self.add_error = cw.error(self,self.frame_add,text="")
        cw.label(self,self.frame_add,text="Direct messages:")
        #self.frame_contacts = cw.frame(self,self.frame_add,expand=1,fill="both",bg="textbox")
        self.frame_contacts = cw.canvas_window(self,self.frame_add)
        self.checking = False

    def guiset(self):
        csg.guiset(self,self.win)

    def switch(self):
        page = self.page.get()
        self.page_title.set(page)
        
        self.label.enable()
        self.label.erase()
        self.label.disable()

        if page == "Posts":
            self.post_frame.pack(fill="both",expand=1,side="right")
            self.msg_frame.pack_forget()
            self.contacts.pack_forget()
            self.frame_add.pack_forget()
            self.error_current = self.error_post
            self.error_current.set("")
        elif page == "Messages":
            self.contacts.pack(fill="y",side="left")
            self.post_frame.pack_forget()
            if self.friend.get() == "add contacts":
                self.frame_add.pack(fill="both",expand=1,side="right")
                self.msg_frame.pack_forget()
                self.page_title.set("Messages - Add contacts")
                self.error_current = self.add_error
                self.error_current.set("")
            else:
                self.msg_frame.pack(fill="both",expand=1,side="right")
                self.frame_add.pack_forget()
                self.chatname = self.friend.get()
                self.error_current = self.error
                self.error_current.set("")
                self.page_title.set("Messages - " + self.master.get_username(self.chatname))
        else:
            self.msg_frame.pack(fill="both",expand=1,side="right")
            self.post_frame.pack_forget()
            self.error_current = self.error
            self.error_current.set("")

        self.master.switch()

class postbtn():
    def __init__(self,i,master) -> None:
        text = master.posts[str(i)]["user"] + "     " + master.posts[str(i)]["date"] + "\n"
        count = 0
        for line in master.posts[str(i)]["msg"].strip().split("\n"):
            if count < 3:
                text += "\n" + line
            else: 
                break
            count += 1

        self.button = cw.button(
                master.gui, master.gui.posts_frame,
                text = text,
                command = self.click,
                fill = "both",
                padx=8,
                pady=8,
                expand=1,
                justify="left",
                anchor="nw",
                bg="bg"
            )
        self.i = i
        self.master = master

    def click(self):
        self.master.chatname = "post" + str(self.i)
        self.master.gui.page.set("Post by " + self.master.posts[str(self.i)]["user"])
        self.master.gui.switch()

class contact_btn():
    def __init__(self,i,master) -> None:
        text = master.get_username(i)
        
        if i not in master.msgs:
            master.msgs[i] = dict()

        #Get and write the last message of the chat
        num = int(master.request(cmd="num",txt=i))
        if num == 0:
            text += "\n\nNo messages"
        else:
            if str(num) not in master.msgs[i]:
                req = master.request(cmd="get",txt=i + "\n" + str(num)).split("\n")
                msg = ""
                for j in req[2:]:
                    msg += j
                
                master.msgs[i][num] = {
                    "user" : req[0],
                    "date" : settings.time_format(req[1]),
                    "msg" : msg
                }
            md = master.msgs[i][num]
            text += "     " + md["date"] + "\n\n" + md["msg"]

        self.button = cw.button(
                master.gui, master.gui.frame_contacts,
                text = text,
                command = self.click,
                fill = "both",
                padx=8,
                pady=8,
                expand=1,
                justify="left",
                anchor="nw",
                bg="bg"
            )
        self.i = i
        self.master = master

    def click(self):
        self.master.gui.friend.set(self.i)
        self.master.gui.switch()
        
def main(master):
    client(master)

if __name__ == "__main__": print("Please run the program through chat_main.py")