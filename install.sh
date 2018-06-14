#!/bin/sh

# install dependencies
sudo apt-get install libusb-1.0-0-dev libudev-dev
sudo apt-get install numpy

git submodule init
git submodule update

cd wii-u-gc-adapter
make
chmod +x wii-u-gc-adapter
sudo cp wii-u-gc-adapter /usr/local/bin
sudo chown root /usr/local/bin/wii-u-gc-adapter

cat << EOF > /tmp/gamecube.service
[Unit]
Description=Wii U Gamecube Adapter
Before=systemd-user-sessions.service

[Service]
TimeoutStartSec=0

ExecStart=/usr/local/bin/wii-u-gc-adapter
User=root

[Install]
WantedBy=multi-user.target
EOF

sudo cp /tmp/gamecube.service /etc/systemd/system/gamecube.service
sudo chown root:root /etc/systemd/system/gamecube.service

sudo modprobe uinput

sudo systemctl enable /etc/systemd/system/gamecube.service
sudo systemctl start gamecube.service
