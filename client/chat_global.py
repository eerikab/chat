'''Global variables to be used by all windows'''

import os

#Versioning
version = "0.0.0" #App version, used later
server_version = ""

#User
user = "" #User name
userid = "" #User ID (16-digit value as string)
password = "" #Password hash
theme = "" #Selected theme
accent = "" #Selected accent
apply_theme = 1 #Whether to apply theming
remember = 1 #Remember username and password hash for next login

#File management
directory = os.path.dirname(__file__)
file_theme = directory+"/config/chat_themes.ini"
file_settings = directory+"/config/chat_settings.txt"

#Locale
months = ["","Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

#Misc
settings_open = 0 #Whether the settings page is open