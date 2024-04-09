import chat_login
import chat_client
import tkinter as tk

class main():
    
    def __init__(self) -> None:
        self.win = tk.Tk()
        self.win.withdraw() #Disable the main window
        self.login()

    def login(self):
        chat_login.main(self)

    def client(self,user,password,userid):
        chat_client.main(user,self,password,userid)

m = main()
m.win.mainloop()