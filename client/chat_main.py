import chat_login
import chat_client
import chat_widgets
import tkinter as tk

'''Main script, use this to run the program
Creates the main window, opens sub-windows'''

class main():
    def __init__(self) -> None:
        self.login()

    def login(self):
        chat_login.main(self)

    def client(self,user,password,userid):
        chat_client.main(user,self,password,userid)

m = main()
#Tkinter widgets customized for this project are centralized in chat_widgets
chat_widgets.root.mainloop()