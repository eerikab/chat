import tkinter as tk
from tkinter import ttk
import chat_settings
import os

'''GUI widgets, automates creating and theming Tkinter widgets
Unifies widgets used by all windows, though they can be individually modified'''

setting = chat_settings.settings()

#Font
font_family = "Noto Sans"
font = (font_family,10)
font_bold = (font_family,10,"bold")

#Lists for configuring
ls_window = []
ls_frame = []
ls_label = []
ls_text = []
ls_button = []
ls_scroll = []
ls_radio = []
ls_entry = []
ls_check = []
ls_comment = []
ls_canvas = []
ls_error = []

def default():
    #Dummy function, does nothing
    pass

#Initialize Tkinter
root = tk.Tk()
root.withdraw() #Disable the main window

class window():
    def __init__(self,window,title="Chat",size="640x480",minsize=(0,0),bg = "bg",close_all=1):
        #Create Tk window
        self.window = window
        self.widget = tk.Toplevel(root)
        self.widget.title(title)
        self.widget.geometry(size)
        self.widget.minsize(minsize[0],minsize[1])
        ls_window.append(self)
        self.color = {"bg" : bg}

        #When pressing the X button on titlebar, end the entire program
        if close_all:
            self.widget.protocol('WM_DELETE_WINDOW', self.destroyall)

    def on_exit(self,command=default):
        self.widget.protocol('WM_DELETE_WINDOW', command)

    def destroy(self):
        self.widget.destroy()

    def destroyall(a=0):
        #End Tkinter session
        root.destroy()

def stringvar(var=""):
    return tk.StringVar(root,var)


#Widgets
#All create the respective Tk widget in one line and return the widget
class frame():
    def __init__(self,window,master,padx=0,pady=0,side="top",expand=0,fill="none",bg = "bg"):
        self.window = window
        self.widget = tk.Frame(master.widget)
        self.pack(padx=padx, pady=pady, side=side, expand=expand, fill=fill)
        ls_frame.append(self)
        self.color = {"bg":bg}

    def pack(self,padx=0,pady=0,side="top",expand=0,fill="none"):
        self.widget.pack(padx=padx, pady=pady, side=side, expand=expand, fill=fill)

    def pack_forget(self):
        self.widget.pack_forget()

class label():
    def __init__(self,window,master,padx=0,pady=0,side="top",expand=0,fill="none",text="",width=0,bg = "bg",fg = "text",bold=False):
        self.window = window
        self.master = master
        if bold:
            fn = font_bold
        else:
            fn = font
        self.widget = tk.Label(master.widget,text=text,font=fn,width=width)
        self.widget.pack(padx=padx, pady=pady, side=side, expand=expand, fill=fill)
        ls_label.append(self)
        self.color = {"bg":bg, "fg":fg}

    def set(self,txt):
        self.widget["text"] = txt

class entry():
    def __init__(self,window,master,padx=0,pady=0,side="top",expand=0,fill="none",width=30,show="",highlightthickness=0,
                 bg = "msg",fg = "text",insertbackground = "text",selectforeground = "text",selectbackground = "high"):
        self.window = window
        self.widget = tk.Entry(master.widget,width=width,show=show,highlightthickness=highlightthickness,font=font)
        self.widget.pack(padx=padx, pady=pady, side=side, expand=expand, fill=fill)
        ls_entry.append(self)
        self.color = {"bg":bg, "fg":fg, "insertbackground":insertbackground, "selectforeground":selectforeground, "selectbackground":selectbackground}

    def insert(self,txt):
        self.widget.insert(0,txt)

    def get(self):
        return self.widget.get().strip()
    
    def clear(self):
        self.widget.delete(0,tk.END)

    def censor(self):
        self.widget.config(show="*")

    def uncensor(self):
        self.widget.config(show="")

class text():
    def __init__(self,window,master,padx=0,pady=0,side="top",expand=0,fill="none",width=20,height=3,highlightthickness=0,borderwidth=1,
                 bg = "textbox",fg = "text",selectbackground = "high",selectforeground = "text",insertbackground = "text",user="user",date="comment"):
        self.window = window
        self.widget = tk.Text(master.widget,width=width,height=height,highlightthickness=highlightthickness,font=font,borderwidth=borderwidth)
        self.widget.pack(padx=padx, pady=pady, side=side, expand=expand, fill=fill)
        ls_text.append(self)
        self.color = {"bg":bg, "fg":fg, "insertbackground":insertbackground, "selectforeground":selectforeground, "selectbackground":selectbackground,
                      "user":user, "date":date}

    def erase(self):
        self.widget.delete(1.0,tk.END)

    def insert(self,txt,args=""):
        self.widget.insert(tk.END,txt,args)
        self.widget.see(tk.END)

    def get(self):
        return self.widget.get(1.0,"end").strip()
    
    def disable(self):
        self.widget.config(state="disabled")

    def enable(self):
        self.widget.config(state="normal")

class button():
    def __init__(self,window,master,padx=0,pady=0,side="top",expand=0,fill="none",text="",highlightthickness=0,command=0,width=0,justify="center",wraplength=0,anchor="center",
                 bg = "button",fg = "text",activebackground = "button_high",activeforeground = "text", i = 0):
        self.window = window
        self.widget = tk.Button(master.widget,text=text,command=command,width=width,highlightthickness=highlightthickness,font=font,justify=justify,wraplength=wraplength,anchor=anchor)
        self.widget.pack(padx=padx, pady=pady, side=side, expand=expand, fill=fill)
        ls_button.append(self)
        self.color = {"bg":bg, "fg":fg, "activebackground":activebackground, "activeforeground":activeforeground}
        self.i = i
        
    def destroy(self):
        ls_button.remove(self)
        self.widget.destroy()

class radio():
    def __init__(self,window,master,padx=0,pady=0,side="top",expand=0,fill="none",text="",value="",variable=0,indicatoron=0,command=default,
            borderwidth=0,padix=0,padiy=0,width=0,highlightthickness=0,bg = "msg",fg = "text",activebackground = "high",activeforeground = "text",selectcolor = "selected"):
        self.window = window
        self.widget = tk.Radiobutton(master.widget,text=text,value=value,variable=variable,indicatoron=indicatoron,borderwidth=borderwidth,
                                padx=padix,pady=padiy,width=width,highlightthickness=highlightthickness,command=command,font=font)
        self.widget.pack(padx=padx, pady=pady, side=side, expand=expand, fill=fill)
        ls_radio.append(self)
        self.color = {"bg":bg, "fg":fg, "activebackground":activebackground, "activeforeground":activeforeground, "selectcolor":selectcolor}

class scroll():
    def __init__(self,window,master,padx=0,pady=0,side="top",expand=0,fill="none",command=default,highlightthickness=0,borderwidth=0,bg="side",troughcolor="textbox",activebackground="high"):
        self.window = window
        self.widget = tk.Scrollbar(master.widget,command=command,highlightthickness=highlightthickness,borderwidth=borderwidth)
        self.widget.pack(padx=padx, pady=pady, side=side, expand=expand, fill=fill)
        ls_scroll.append(self)
        self.color = {"bg":bg, "activebackground":activebackground, "troughcolor":troughcolor}

class check():
    def __init__(self,window,master,padx=0,pady=0,side="top",expand=0,fill="none",text="",highlightthickness=0,command=default,
                 bg = "bg",fg = "text",activebackground = "high",activeforeground = "text",selectcolor = "msg",activecolor = "button"):
        self.variable = tk.IntVar()
        self.window = window
        self.widget = tk.Checkbutton(master.widget,text=text,variable=self.variable,highlightthickness=highlightthickness,command=command,font=font)
        self.widget.pack(padx=padx, pady=pady, side=side, expand=expand, fill=fill)
        ls_check.append(self)
        self.color = {"bg":bg, "fg":fg, "activebackground":activebackground, "activeforeground":activeforeground, "selectcolor":selectcolor, "activecolor":activecolor}

class comment(label):
    def __init__(self,window,master,padx=0,pady=0,side="top",expand=0,fill="none",text="",bg = "bg",fg = "comment"):
        self.window = window
        self.master = master
        self.widget = tk.Label(master.widget,text=text,font=font)
        self.widget.pack(padx=padx, pady=pady, side=side, expand=expand, fill=fill)
        ls_comment.append(self)
        self.color = {"bg":bg, "fg":fg}

class error(label):
    def __init__(self,window,master,padx=0,pady=0,side="top",expand=0,fill="none",text="",bg = "bg",fg = "error"):
        self.window = window
        self.master = master
        self.widget = tk.Label(master.widget,text=text,font=font)
        self.widget.pack(padx=padx, pady=pady, side=side, expand=expand, fill=fill)
        ls_comment.append(self)
        self.color = {"bg":bg, "fg":fg}

class canvas():
    def __init__(self,window,master,padx=0,pady=0,side="top",expand=0,fill="none",highlightthickness=0,bg="textbox"):
        self.window = window
        self.widget = tk.Canvas(master.widget,highlightthickness=highlightthickness,)
        self.widget.pack(padx=padx, pady=pady, side=side, expand=expand, fill=fill)
        ls_canvas.append(self)
        self.color = {"bg":bg} 

class canvas_window():
    def __init__(self,window,master) -> None:
        canvas_frame = frame(window,master,fill="both",expand=1)

        self.canvas = canvas(window,canvas_frame,fill="both",expand=1,side="left")
        scrollbar = scroll(window,canvas_frame,
                                      command=self.canvas.widget.yview,
                                      side="right",
                                      fill="y")

        self.canvas.widget.configure(yscrollcommand=scrollbar.widget.set)
        canvas_frame = frame(window,self.canvas,fill="both",expand=1,bg="textbox")

        self.widget = canvas_frame.widget

        self.canvas.widget.bind("<Configure>", 
                            lambda e: self.canvas.widget.configure(scrollregion = self.widget.bbox()))
        
        self.canvas.widget.bind("<Configure>", self.post_region)
        self.canvas.widget.bind("<Configure>", self.fill_width)

        self.frame_id = self.canvas.widget.create_window(self.canvas.widget.winfo_width(),0,window=self.widget,anchor="nw")

        #self.post_region()


    def post_region(self):
        self.canvas.widget.configure(scrollregion = self.canvas.widget.bbox("all"))

    def fill_width(self,event):
        width = event.width
        self.canvas.widget.itemconfigure(self.frame_id, width=self.canvas.widget.winfo_width())

#Theming
def theming(window,_theme,_accent):
    '''Get theme colours'''
    theme = setting.theming(_theme,_accent)

    #Update widget colours
    for i in ls_frame:
        try:
            if i.window == window:
                i.widget.config(bg = theme[i.color["bg"]])
        except Exception as e:
            print(e) 
    for i in ls_label:
        try:
            if i.window == window:
                i.widget.config(bg = theme[i.master.color["bg"]],
                    fg = theme[i.color["fg"]])
        except Exception as e:
            print(e) 
    for i in ls_comment:
        try:
            if i.window == window:
                i.widget.config(bg = theme[i.color["bg"]],
                    fg = theme[i.color["fg"]])
        except Exception as e:
            print(e)
    for i in ls_error:
        try:
            if i.window == window:
                i.widget.config(bg = theme[i.master.color["bg"]],
                    fg = theme[i.color["fg"]])
        except Exception as e:
            print(e) 
    for i in ls_button:
        try:
            if i.window == window:
                i.widget.config(bg = theme[i.color["bg"]],
                    fg = theme[i.color["fg"]],
                    activebackground = theme[i.color["activebackground"]],
                    activeforeground = theme[i.color["activeforeground"]])
        except Exception as e:
            print(e) 
    for i in ls_check:
        try:
            if i.window == window:
                i.widget.config(bg = theme[i.color["bg"]],
                    fg = theme[i.color["fg"]],
                    activebackground = theme[i.color["activebackground"]],
                    activeforeground = theme[i.color["activeforeground"]],
                    selectcolor = theme[i.color["selectcolor"]])
                if i.variable.get():
                    i.widget["selectcolor"] = theme[i.color["activecolor"]]
        except Exception as e:
            print(e) 
    for i in ls_entry:
        try:
            if i.window == window:
                i.widget.config(bg = theme[i.color["bg"]],
                    fg = theme[i.color["fg"]],
                    insertbackground = theme[i.color["insertbackground"]],
                    selectforeground = theme[i.color["selectforeground"]],
                    selectbackground = theme[i.color["selectbackground"]])
        except Exception as e:
            print(e) 
    for i in ls_text:
        try:
            if i.window == window:
                i.widget.config(bg = theme[i.color["bg"]],
                    fg = theme[i.color["fg"]],
                    selectbackground = theme[i.color["selectbackground"]],
                    selectforeground = theme[i.color["selectforeground"]],
                    insertbackground = theme[i.color["insertbackground"]])
                i.widget.tag_configure("User",foreground=theme[i.color["user"]] , font=font_bold)
                i.widget.tag_configure("Date",foreground=theme[i.color["date"]])
        except Exception as e:
            print(e) 
    for i in ls_radio:
        try:
            if i.window == window:
                i.widget.config(bg = theme[i.color["bg"]],
                    fg = theme[i.color["fg"]],
                    activebackground = theme[i.color["activebackground"]],
                    activeforeground = theme[i.color["activeforeground"]],
                    selectcolor = theme[i.color["selectcolor"]])
        except Exception as e:
            print(e) 
    for i in ls_scroll:
        try:
            if i.window == window:
                i.widget.config(bg = theme[i.color["bg"]],
                    troughcolor = theme[i.color["troughcolor"]],
                    activebackground = theme[i.color["activebackground"]])
        except Exception as e:
            print(e) 
    for i in ls_canvas:
        try:
            if i.window == window:
                i.widget.config(bg = theme[i.color["bg"]])
        except Exception as e:
            print(e)
    for i in ls_window:
        try:
            if i.window == window:
                i.widget.config(bg = theme[i.color["bg"]])
        except Exception as e:
            print(e)