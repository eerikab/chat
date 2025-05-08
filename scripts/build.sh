#!/bin/bash

# Build an executable of desktop client
# Add chat_themes.json as a dependency
# Hide the console on Windows
python3 -m PyInstaller ../client/chat_main.py --add-data=../client/config/chat_themes.json:config/ --noconsole
