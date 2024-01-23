import socket
import tkinter as tk

win = tk.Tk()

delay = 1000
run = 1
success = 0

class client():
    def __init__(self) -> None:
        self.welcome = tk.Label(win,text="Welcome!")
        self.welcome.pack()
        self.name_label = tk.Label(win, text="Please write your nickname:")
        self.name_label.pack()
        self.name = tk.Entry(win,width=25)
        self.name.pack(padx=16)
        self.name_label2 = tk.Label(win, text="This will be the name under which your messages will be sent")
        self.name_label2.pack(padx=16)

        #self.password_label = tk.Label(win, text="Password:")
        #self.password_label.pack()
        #self.password = tk.Entry(win)
        #self.password.pack()

        self.remember = tk.Checkbutton(win,text="Remember me")
        self.remember.pack()

        self.send = tk.Button(win, text="Login", command=self.submit)
        self.send.pack()
        self.error = tk.Label(win,fg="red")
        self.error.pack()
        self.join()
    
    def join(self):
        try:
            self.c = socket.socket()
            self.c.connect(("localhost",9999))
            return 1
        except:
            self.error["text"] = "Could not connect to server"
            return 0

    def submit(self):
        self.error["text"] = ""
        user = self.name.get().strip()
        global success
        if self.join():
            self.c.send(bytes("login\n"+user,"utf-8"))
            resp = self.c.recv(1024).decode()
            if resp == "OK":
                success = 1
                win.destroy()
            else:
                self.error["text"] = resp

def main():
    global success
    cl = client()

    win.mainloop()
    if success:
        return cl.name.get()
    else:
        return ""
    
if __name__ == "__main__": main()