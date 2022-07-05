#!/bin/sh env

sudo pacman -S python-pip
yay -Syu chromium-widevine
pip3 install -r requirements.txt

#pip3 install PyQt5
#pip3 install PyQt5-tools
#pip3 insatll QWebEngineView
#pip3 install pyaudio
#pip3 insatll wave
#pip3 insatll spotipy
#pip3 install PyQt5-stubs