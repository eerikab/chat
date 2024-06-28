import tkinter as tk
from tkinter import ttk
import chat_settings
import os

'''GUI widgets, automates creating and theming Tkinter widgets
Unifies widgets used by all windows, though they can be individually modified'''

setting = chat_settings.settings()

font = os.path.dirname(__file__)+"/fonts/Cantarell.ttf 10"
font_bold = os.path.dirname(__file__)+"/fonts/Cantarell-Bold.ttf 10"

#Lists for configuring
ls_frame = dict()
ls_label = dict()
ls_text = dict()
ls_button = dict()
ls_scroll = dict()
ls_radio = dict()
ls_entry = dict()
ls_check = dict()
ls_comment = dict()
ls_canvas = dict()

def theme_init(window):
    ls_frame[window] = []
    ls_label[window] = []
    ls_text[window] = []
    ls_button[window] = []
    ls_scroll[window] = []
    ls_radio[window] = []
    ls_entry[window] = []
    ls_check[window] = []
    ls_comment[window] = []
    ls_canvas[window] = []

def default():
    #Dummy function, does nothing
    pass

#Widgets
#All create the respective Tk widget in one line and return the widget
def frame(window,master,padx=0,pady=0,side="top",expand=0,fill="none"):
    widget = tk.Frame(master)
    widget.pack(padx=padx, pady=pady, side=side, expand=expand, fill=fill)
    ls_frame[window].append(widget)
    return widget

def label(window,master,padx=0,pady=0,side="top",expand=0,fill="none",text="",width=0):
    widget = tk.Label(master,text=text,font=font,width=width)
    widget.pack(padx=padx, pady=pady, side=side, expand=expand, fill=fill)
    ls_label[window].append(widget)
    return widget

def entry(window,master,padx=0,pady=0,side="top",expand=0,fill="none",width=20,show="",highlightthickness=0):
    widget = tk.Entry(master,width=width,show=show,highlightthickness=highlightthickness,font=font)
    widget.pack(padx=padx, pady=pady, side=side, expand=expand, fill=fill)
    ls_entry[window].append(widget)
    return widget

def text(window,master,padx=0,pady=0,side="top",expand=0,fill="none",width=20,height=3,highlightthickness=0,borderwidth=1):
    widget = tk.Text(master,width=width,height=height,highlightthickness=highlightthickness,font=font,borderwidth=borderwidth)
    widget.pack(padx=padx, pady=pady, side=side, expand=expand, fill=fill)
    ls_text[window].append(widget)
    return widget

def button(window,master,padx=0,pady=0,side="top",expand=0,fill="none",text="",highlightthickness=0,command=0,width=0,justify="center",wraplength=0,anchor="center"):
    widget = tk.Button(master,text=text,command=command,width=width,highlightthickness=highlightthickness,font=font,justify=justify,wraplength=wraplength,anchor=anchor)
    widget.pack(padx=padx, pady=pady, side=side, expand=expand, fill=fill)
    ls_button[window].append(widget)
    return widget

def radio(window,master,padx=0,pady=0,side="top",expand=0,fill="none",text="",value="",variable=0,indicatoron=0,
          borderwidth=0,padix=0,padiy=0,width=0,highlightthickness=0,command=default):
    widget = tk.Radiobutton(master,text=text,value=value,variable=variable,indicatoron=indicatoron,borderwidth=borderwidth,
                            padx=padix,pady=padiy,width=width,highlightthickness=highlightthickness,command=command,font=font)
    widget.pack(padx=padx, pady=pady, side=side, expand=expand, fill=fill)
    ls_radio[window].append(widget)
    return widget

def scroll(window,master,padx=0,pady=0,side="top",expand=0,fill="none",command=default,highlightthickness=0,borderwidth=0):
    widget = tk.Scrollbar(master,command=command,highlightthickness=highlightthickness,borderwidth=borderwidth)
    widget.pack(padx=padx, pady=pady, side=side, expand=expand, fill=fill)
    ls_scroll[window].append(widget)
    return widget

def check(window,master,padx=0,pady=0,side="top",expand=0,fill="none",text="",variable=0,highlightthickness=0,command=default):
    widget = tk.Checkbutton(master,text=text,variable=variable,highlightthickness=highlightthickness,command=command,font=font)
    widget.pack(padx=padx, pady=pady, side=side, expand=expand, fill=fill)
    ls_check[window].append(widget)
    return widget

def comment(window,master,padx=0,pady=0,side="top",expand=0,fill="none",text=""):
    widget = tk.Label(master,text=text,font=font)
    widget.pack(padx=padx, pady=pady, side=side, expand=expand, fill=fill)
    ls_comment[window].append(widget)
    return widget

def canvas(window,master,padx=0,pady=0,side="top",expand=0,fill="none",highlightthickness=0):
    widget = tk.Canvas(master,highlightthickness=highlightthickness)
    widget.pack(padx=padx, pady=pady, side=side, expand=expand, fill=fill)
    ls_canvas[window].append(widget)
    return widget

#Theming
def theming(window,_theme,_accent):
    '''Get theme colours'''
    theme, accent = setting.theming(_theme,_accent)
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

    #Update widget colours
    for i in ls_frame[window]:
        try:
            i.config(bg = col_bg)
        except: pass
    for i in ls_label[window]:
        try:
            i.config(bg = col_bg,
                    fg = col_text)
        except: pass
    for i in ls_comment[window]:
        try:
            i.config(bg = col_bg,
                    fg = col_comment)
        except: pass
    for i in ls_button[window]:
        try:
            i.config(bg = col_button,
                    fg = col_text,
                    activebackground = col_button_high,
                    activeforeground = col_text)
        except: pass
    for i in ls_check[window]:
        try:
            i.config(bg = col_bg,
                    fg = col_text,
                    activebackground = col_high,
                    activeforeground = col_text,
                    selectcolor = col_msg)
            if i["variable"] == 1:
                i["selectcolor"] = col_button
            else:
                i["selectcolor"] = col_msg
        except: pass
    for i in ls_entry[window]:
        try:
            i.config(bg = col_msg,
                    fg = col_text,
                    insertbackground = col_text,
                    selectforeground = col_text,
                    selectbackground = col_high)
        except: pass
    for i in ls_text[window]:
        try:
            i.config(bg = col_textbox,
                    fg = col_text,
                    selectbackground = col_high,
                    selectforeground = col_text,
                    insertbackground = col_text)
        except: pass
    for i in ls_radio[window]:
        try:
            i.config(bg = col_msg,
                    fg = col_text,
                    activebackground = col_high,
                    activeforeground = col_text,
                    selectcolor = col_select)
        except: pass
    for i in ls_scroll[window]:
        try:
            i.config(bg=col_side,
                 troughcolor=col_textbox,
                 activebackground=col_high)
        except: pass
    for i in ls_canvas[window]:
        try:
            i.config(bg = col_textbox)
        except: pass
        
    return theme, accent