import os
import configparser
import tkinter as tk

class settings():
    def __init__(self,master="") -> None:
        self.file_theme = os.path.dirname(__file__)+"/chat_themes.ini"
        self.file_settings = os.path.dirname(__file__)+"/chat_settings.txt"
        self.font = os.path.dirname(__file__)+"/fonts/Cantarell.ttf"
        self.font_bold = os.path.dirname(__file__)+"/fonts/Cantarell-Bold.ttf"
        self.master = master #Main class for responding

        #Create settings file if not available
        try:
            with open(self.file_theme,"r"):
                pass
        except:
            self.reset()

        self.reset()

        #Open config file for reading
        config = configparser.ConfigParser()
        config.read(self.file_theme)

        #Get theme settings
        self.themelist = []
        i = 1
        while True:
            sect = "Theme "+str(i)
            if config.has_section(sect):
                theme = {
                    "name" : config.get(sect,"Name"),
                    "bg" : config.get(sect,"Background"),
                    "textbox" : config.get(sect,"Textbox"),
                    "msg" : config.get(sect,"Messagebox"),
                    "side" : config.get(sect,"Sidebar"),
                    "text" : config.get(sect,"Text"),
                    "high" : config.get(sect,"Highlight"),
                    "high_text" : config.get(sect,"Highlight text")
                }
                self.themelist.append(theme)
                i+=1
            else:
                break

        self.accentlist = []
        i = 1
        while True:
            sect = "Accent "+str(i)
            if config.has_section(sect):
                accent = {
                    "name" : config.get(sect,"Name"),
                    "button" : config.get(sect,"Button"),
                    "user" : config.get(sect,"User"),
                    "button_high" : config.get(sect,"Button highlight"),
                    "selected" : config.get(sect,"Selected option"),
                }
                self.accentlist.append(accent)
                i+=1
            else:
                break

        self.theme_names = []
        for i in self.themelist:
                self.theme_names.append(i["name"])

        self.accent_names = []
        for i in self.accentlist:
                self.accent_names.append(i["name"])

        self.themed = 0

    def reset(self):
        #Reset all themes
        with open(self.file_theme,"w") as settings:
            config = configparser.ConfigParser()
            '''config["Themes"] = {
                "Theme 1" : "Dark",
                "Theme 2" : "Light",
                "Accent 1" : "Blue",
                "Accent 2" : "Green",
                "Accent 3" : "Orange",
                "Accent 4" : "Red",
                "Accent 5" : "Purple"
            }'''

            config["Theme 1"] = {
                "Name" : "Dark",
                "Background" : "#333333",
                "Textbox" : "#1e1e1e",
                "Messagebox" : "#3f3f3f",
                "Sidebar" : "#3f3f3f",
                "Text" : "#f2f2f2",
                "Highlight" : "#5a5a5a",
                "Highlight text" : "#f2f2f2"
            }
            config["Theme 2"] = {
                "Name" : "Light",
                "Background" : "#ececec",
                "Textbox" : "#fafafa",
                "Messagebox" : "#dcdcdc",
                "Sidebar" : "#dcdcdc",
                "Text" : "#202020",
                "Highlight" : "#c8c8c8",
                "Highlight text" : "#202020"
            }
            config["Accent 1"] = {
                "Name" : "Blue",
                "Button" : "#008cff",
                "User" : "#00c8b7",
                "Button highlight" : "#00aaff",
                "Selected option" : "#00a0ff",
            }
            config["Accent 2"] = {
                "Name" : "Green",
                "Button" : "#1caa00",
                "User" : "#00c01a",
                "Button highlight" : "#21c800",
                "Selected option" : "#1eb400",
            }
            config["Accent 3"] = {
                "Name" : "Orange",
                "Button" : "#f07000",
                "User" : "#f06000",
                "Button highlight" : "#ff8000",
                "Selected option" : "#f07800",
            }
            config["Accent 4"] = {
                "Name" : "Red",
                "Button" : "#f00028",
                "User" : "#f00054",
                "Button highlight" : "#ff2030",
                "Selected option" : "#f5002a",
            }
            config["Accent 5"] = {
                "Name" : "Purple",
                "Button" : "#b400f0",
                "User" : "#ff00ff",
                "Button highlight" : "#c040ff",
                "Selected option" : "#bc00fa",
            }
            config.write(settings)

    def theming(self,theme_sect="",accent_sect=""):
        config = configparser.ConfigParser()
        config.read(self.file_theme)
        sect = theme_sect
        theme = self.themelist[0]
        for i in self.themelist:
            if i["name"] == sect:
                theme = i
        sect = accent_sect
        accent = self.accentlist[0]
        for i in self.accentlist:
            if i["name"] == sect:
                accent = i
        return theme, accent

    def local_theming(self,list_frame=[],list_label=[],list_button=[],list_radio=[]):
        #Function used to theme local settings window
        for i in [self.ls_button,self.ls_label,self.ls_text,self.ls_check,self.ls_radio]:
            for j in i:
                j["font"] = self.font + " 10"
        
        if self.check_var.get() or self.themed:
            #Get theme colours
            theme, accent = self.theming(self.theme_var.get(),self.accent_var.get())
            #print("Theming",self.theme_var.get(),self.accent_var.get())
            col_bg = theme["bg"]
            col_textbox = theme["textbox"]
            col_msg = theme["msg"]
            col_side = theme["side"]
            col_text = theme["text"]
            col_high = theme["high"]
            col_high_text = theme["high_text"]

            col_button = accent["button"]
            col_user = accent["user"] 
            col_button_high = accent["button_high"]
            col_select = accent["selected"]

            #Update widget colours
            for i in self.ls_frame:
                i.config(bg = col_bg)
            for i in self.ls_label:
                i.config(bg = col_bg,
                         fg = col_text)
            for i in self.ls_button:
                i.config(bg = col_button,
                         fg = col_text,
                         activebackground = col_button_high,
                         activeforeground = col_text)
            for i in self.ls_radio:
                i.config(bg = col_msg,
                         fg = col_text,
                         activebackground = col_high,
                         activeforeground = col_text,
                         selectcolor = col_select)
            for i in self.ls_text:
                i.config(bg = col_textbox,
                         fg = col_text,
                         selectbackground = col_high,
                         selectforeground = col_text,
                         insertbackground = col_text)
            for i in self.ls_check:
                i.config(bg = col_bg,
                         fg = col_text,
                         activebackground = col_high,
                         activeforeground = col_text)
                if self.check_var.get():
                    i["selectcolor"] = col_button
                else:
                    i["selectcolor"] = col_msg

            self.field.tag_configure("User",foreground=col_user,font=self.font+" 10 bold")
            self.error["fg"] = "red"

            self.error["text"] = ""
            self.themed = 1
            
        
        if self.check_var.get() == 0 and self.themed:
            self.error["text"] = "Please restart to disable theming"

    def guiset(self,window=""):
        #Theming
        try:
            with open(self.file_settings,"r") as file:
                lines = file.readlines()
                print(lines)
                self.user = lines[0].strip()
                self.password = lines[1].strip()
                self.theme = lines[2].strip()
                self.accent = lines[3].strip()
                self.theme_apply = int(lines[4].strip())
        except:
            self.user = ""
            self.password = ""
            self.theme = ""
            self.accent = ""
            self.theme_apply = 1

        #Create window
        if window == "":
            self.win = tk.Tk()
        else:
            self.win = tk.Toplevel(window)

        self.win.title("Chat settings")
        self.theme_var = tk.StringVar(self.win)
        self.theme_var.set(self.themelist[0]["name"])
        self.accent_var = tk.StringVar(self.win)
        self.accent_var.set(self.accentlist[0]["name"])
        self.check_var = tk.IntVar(self.win)
        self.check_var.set(self.theme_apply)

        #Lists for managing widget themes
        self.ls_frame = []
        self.ls_label = []
        self.ls_radio = []
        self.ls_button = []
        self.ls_text = []
        self.ls_check = []

        #print(self.theme)
        frame = tk.Frame(self.win)
        frame.pack(expand=1,fill="both")
        self.ls_frame.append(frame)
        theme_text = tk.Label(frame,text="Theme:",width=50)
        theme_text.pack()
        self.ls_label.append(theme_text)
        for i in self.themelist:
            name = i["name"]
            theme_select = tk.Radiobutton(frame, 
                                        text=name, 
                                        value=name, 
                                        variable=self.theme_var,
                                        indicatoron=0,
                                        borderwidth=0,
                                        pady=4,
                                        width=20,
                                        highlightthickness=0,
                                        command=self.local_theming
                                        )
            theme_select.pack()
            self.ls_radio.append(theme_select)
            if name == self.theme:
                self.theme_var.set(name)
        

        accent_text = tk.Label(frame,text="Accent Color:")
        accent_text.pack()
        self.ls_label.append(accent_text)
        for i in self.accentlist:
            name = i["name"]
            accent_select = tk.Radiobutton(frame, 
                                        text=name, 
                                        value=name, 
                                        variable=self.accent_var,
                                        indicatoron=0,
                                        borderwidth=0,
                                        pady=4,
                                        width=20,
                                        highlightthickness=0,
                                        command=self.local_theming
                                        )
            accent_select.pack()
            self.ls_radio.append(accent_select)
            if name == self.accent:
                self.accent_var.set(name)

        theme_check = tk.Checkbutton(frame,variable=self.check_var,text="Apply theming",highlightthickness=0,command=self.local_theming)
        theme_check.pack(pady=8)
        self.ls_check.append(theme_check)

        self.field = tk.Text(frame,width=50,height=3,highlightthickness=0,borderwidth=0)
        self.field.insert(tk.END,"User: ","User")
        self.field.insert(tk.END,"Sample message")
        self.field.pack(padx=16)
        self.ls_text.append(self.field)
        
        self.error = tk.Label(frame,fg="red")
        self.error.pack()
        self.ls_label.append(self.error)

        frame_bottom = tk.Frame(frame)
        frame_bottom.pack(fill="both",expand=1)
        self.ls_frame.append(frame_bottom)
        frame_bottom_left = tk.Frame(frame_bottom)
        frame_bottom_left.pack(fill="both",expand=1,side="left")
        self.ls_frame.append(frame_bottom_left)
        frame_bottom_right = tk.Frame(frame_bottom)
        frame_bottom_right.pack(fill="both",expand=1,side="right")
        self.ls_frame.append(frame_bottom_right)

        button_ok = tk.Button(frame_bottom_left,
                            text="OK",
                            highlightthickness=0,
                            command=self.gui_ok)
        button_ok.pack(pady=8)
        self.ls_button.append(button_ok)
        button_cancel = tk.Button(frame_bottom_right,
                                text="Cancel",
                                highlightthickness=0,
                                command=self.gui_close)
        
        button_cancel.pack(pady=8)
        self.ls_button.append(button_cancel)
        self.inloop = 1
        self.themed = 0

        self.local_theming()

        print(self.theme_var.get(),self.accent_var.get())

        if __name__ == "__main__":
            self.win.mainloop()

        return self.theme_var.get(), self.accent_var.get()

    def gui_close(self):
        self.win.destroy()

    def gui_ok(self):
        user = ""
        password = ""
        self.win.destroy()
        try:
            with open(self.file_settings,"r") as file:
                lines = file.readlines()
                user = lines[0].strip()
                password = lines[1].strip()
        finally:
            with open(self.file_settings,"w") as file:
                file.write(user)
                file.write("\n"+password)
                file.write("\n"+self.theme_var.get())
                file.write("\n"+self.accent_var.get())
                file.write("\n"+str(self.check_var.get()))
            if self.master != "":
                self.master.theming()

if __name__ == "__main__":
    gui = settings()
    gui.guiset()