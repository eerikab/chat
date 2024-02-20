import os
import chat_login
import chat_client
import tkinter as tk

directory = os.path.dirname(__file__)

def main():
    user = chat_login.main()

    if user != "":
        if chat_client.main(user):
            main()

main()