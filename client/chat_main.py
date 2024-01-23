import os
import chat_login

directory = os.path.dirname(__file__)+"/chatserverlog.txt"

user = chat_login.main()

if user != "":
    import chat_client
    chat_client.main(user)