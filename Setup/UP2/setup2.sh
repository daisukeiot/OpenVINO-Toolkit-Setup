#!/bin/bash

# Uninstall some apps to save disk space
sudo apt-get remove -y --purge libreoffice* aisleriot gnome-sudoku *mahjongg ace-of-penguins gnomine gbrainy 
sudo apt-get clean 
sudo apt-get autoremove -y 
# Install UP firmware
sudo apt-get install -y firmware-ampak 
sudo apt-get install upboard-extras 
sudo usermod -a -G gpio ${USER} 
sudo usermod -a -G leds ${USER} 
sudo usermod -a -G dialout ${USER} 
sudo reboot
