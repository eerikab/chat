'''Graphical interface for the main window for chatting rooms and messages'''

import chat_settings as settings
import chat_widgets as cw
import chat_settings_gui as csg
import chat_global as cg

class client():
    def __init__(self,master) -> None:

        #Initialise window
        self.win = cw.window(self,cg.app_name,"800x600",(640,480))
        self.master = master

        self.page = cw.stringvar("Messages")
        self.friend = cw.stringvar("main")

        self.sidebar = 1

        #Create widgets
        self.right = cw.frame(self,self.win,side="right",fill="both",expand=1)
        self.left = cw.frame(self,self.win,side="left",fill="y",bg="sidebar")

        self.titlebar = cw.frame(self,self.right,fill="x")

        self.button_menu_frame = cw.frame(self,self.titlebar,side="left",width=1)
        self.button_menu_right = cw.button(self,self.button_menu_frame,text="Menu",command=self.toggle_sidebar,pady=4)
        self.button_menu_right.widget.pack_forget()
        
        self.page_title = cw.label(self,self.titlebar,text="Page",side="left",padx=8,fg="selected_option",bold=True,pady=8)
        #self.search = cw.entry(self,self.titlebar,side="right",pady=8,padx=8)
        #cw.label(self,self.titlebar,text="Search:",side="right")

        self.page_frame = cw.frame(self,self.right,expand=1,fill="both")

        self.title_frame = cw.frame(self,self.left,pady=4,fill="x",bg="sidebar")
        self.title = cw.label(self,self.title_frame, text=cg.app_name,pady=4,bold=True,fg="selected_option",side="right",fill="x", expand=1)
        self.button_menu_left = cw.button(self,self.title_frame,text="Menu",command=self.toggle_sidebar,pady=0,side="left")

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
                                 bg="messagebox"
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
                                 bg="messagebox"
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
        self.contacts_default = self.user_label("No contacts found")
        self.checking = False

    def post_label(self,txt):
        frame = cw.frame(self,self.posts_frame,fill="x",bg="textbox")
        cw.comment(self,frame,text=txt,side="left",padx=8)
        return frame
    
    def user_label(self,txt):
        frame = cw.frame(self,self.frame_contacts,fill="x",bg="textbox")
        cw.comment(self,frame,text=txt,side="left",padx=8)
        return frame

    def guiset(self):
        csg.guiset(self,self.win)

    def switch(self):
        page = self.page.get()
        self.set_title(page)
        
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
                self.set_title("Messages - Add contacts")
                self.error_current = self.add_error
                self.error_current.set("")
            else:
                self.msg_frame.pack(fill="both",expand=1,side="right")
                self.frame_add.pack_forget()
                self.chatname = self.friend.get()
                self.error_current = self.error
                self.error_current.set("")
                self.set_title("Messages - " + self.master.get_username(self.chatname))
        else:
            self.msg_frame.pack(fill="both",expand=1,side="right")
            self.post_frame.pack_forget()
            self.error_current = self.error
            self.error_current.set("")

        self.master.switch()

    def set_title(self, txt):
        self.page_title.set(txt)
        self.win.title(cg.app_name+" - " +txt)

    def toggle_sidebar(self):
        self.sidebar = not self.sidebar
        if self.sidebar:
            self.left.pack(side="left",fill="y")
            self.button_menu_right.widget.pack_forget()
            self.button_menu_frame.widget["width"] = 1
            if self.page.get() == "Messages":
                self.contacts.pack(fill="y",side="left")
            
        else:
            self.left.pack_forget()
            self.contacts.pack_forget()
            self.button_menu_right.widget.pack(pady=4)
            self.button_menu_frame.widget["width"] = 0


class postbtn():
    def __init__(self,i,master) -> None:
        count = 0
        msg = ""
        
        for line in master.posts[str(i)]["msg"].strip().split("\n"):
            if count < 3:
                msg += "\n" + line
            else: 
                break
            count += 1

        self.widget = cw.text_button(
                master.gui, master.gui.posts_frame,
                command = self.click,
                height = count+2,
                text_user = master.posts[str(i)]["user"],
                text_date = master.posts[str(i)]["date"] + "     " + str(master.posts[str(i)]["length"]-1) + " replies",
                msg = msg
            )
        self.i = i
        self.master = master

    def click(self,event=""):
        self.master.chatname = "post" + str(self.i)
        self.master.gui.page.set("Post by " + self.master.posts[str(self.i)]["user"])
        self.master.gui.switch()

class contact_btn():
    def __init__(self,i,master) -> None:
        user = master.get_username(i)
        date = ""
        msg = ""
        
        if i not in master.msgs:
            master.msgs[i] = dict()

        #Get and write the last message of the chat
        num = int(master.request(cmd="num",txt=i))
        if num == 0:
            msg = "No messages"
        else:
            if str(num) not in master.msgs[i]:
                req = master.request(cmd="get",txt=i + "\n" + str(num) + "\n" + str(num))
                msgs = settings.json_decode(req)
                
                master.msgs[i][num] = {
                    "user" : msgs[0][1],
                    "date" : settings.time_format(msgs[0][2]),
                    "msg" : msgs[0][3].strip()
                }
            md = master.msgs[i][num]
            date = md["date"]
            msg = md["msg"]

        self.widget = cw.text_button(
                master.gui, master.gui.frame_contacts,
                command = self.click,
                text_user = user,
                text_date = date,
                msg = "\n" + msg.split("\n")[0]
            )
        self.i = i
        self.master = master

    def click(self, event=""):
        self.master.gui.friend.set(self.i)
        self.master.gui.switch()
        
def main(master):
    client(master)

if __name__ == "__main__": print("Please run the program through chat_main.py")