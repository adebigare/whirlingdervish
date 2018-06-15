#!/usr/bin/python

#also written by dlaw. see license in lights.py

import colorsys, time
from lights import PowerSupply
from evdev import InputDevice, categorize, ecodes

FRAMERATE = 30.0
PAD_PATH = "/dev/input/by-id/usb-mayflash_limited_MAYFLASH_GameCube_Controller_Adapter-event-joystick"

pad = InputDevice(PAD_PATH)
pds = PowerSupply('192.168.0.101')
hue = 0

print(pad)

def update_hue(hue):
    color = colorsys.hsv_to_rgb(hue, 1, 1)
    pds.set_all(color)
    pds.update()


for event in pad.read_loop():
    if event.type == ecodes.EV_KEY and event.value == 1:
        if event.code == 300: #up
            update_hue(0.0)
        if event.code == 301: #right
            update_hue(0.2)
        if event.code == 302: #down
            update_hue(0.4)
        if event.code == 303: #left
            update_hue(0.6)
