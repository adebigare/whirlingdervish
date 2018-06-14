#!/bin/sh

# install dependencies
sudo apt-get install libusb-1.0-0-dev libudev-dev
sudo apt-get install numpy

cd wii-u-gc-adapter
make
chmod +x wii-u-gc-adapter
sudo cp wii-u-gc-adapter /usr/local/bin
sudo chown root /usr/local/bin/wii-gc-adapter

sudo modprobe uinput
