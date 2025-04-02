#!/bin/bash

# Build an executable of desktop client
# Add chat_themes.ini as a dependency
# Hide the console on Windows
python -m PyInstaller ../client/chat_main.py --add-data=../client/config/chat_themes.ini:config/ --noconsole
