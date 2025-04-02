'''Global variables to be used by all windows'''

import os

#Connection
release = 1 #Release/Debug flag, 0 is for localhost, 1 for public ip
HOST, PORT = "ws://localhost", 9000

if release:
    HOST, PORT = "wss://chat-4zh4.onrender.com", "" #Server IP for released application

#Versioning
app_name = "TickChat"
version = "0.1.4" #App version, increase with each released update
server_version = ""

#User
user = "" #User name
userid = "" #User ID (16-digit value as string)
password = "" #Password hash
theme = "" #Selected theme
accent = "" #Selected accent
apply_theme = 1 #Whether to apply theming
remember = 1 #Remember username and password hash for next login
session = "" #Session ID

#File management
directory = os.path.dirname(__file__)
file_theme = directory+"/config/chat_themes.ini"
file_settings = directory+"/config/chat_settings.txt"

#Locale
months = ["","Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

#Misc
settings_open = 0 #Whether the settings page is open