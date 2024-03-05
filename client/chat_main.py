import os
import chat_login
import chat_client
import tkinter as tk

directory = os.path.dirname(__file__)

class main():
    
    def __init__(self) -> None:
        self.win = tk.Tk()
        self.win.withdraw() #Disable the main window
        self.login()

    def login(self):
        chat_login.main(self)

    def client(self,user):
       chat_client.main(user,self)

m = main()
m.win.mainloop()