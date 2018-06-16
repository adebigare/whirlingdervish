#!/usr/bin/python

#also written by dlaw. see license in lights.py

import colorsys
from time import sleep
from lights import PowerSupply
from evdev import InputDevice, categorize, ecodes
from threading import Thread
from Queue import Queue

FRAMERATE = 30.0
PAD_PATH = "/dev/input/by-id/usb-mayflash_limited_MAYFLASH_GameCube_Controller_Adapter-event-joystick"

pad = InputDevice(PAD_PATH)
pds = PowerSupply('192.168.0.101')
events = Queue()

def handle_event(event):
    if event.type == ecodes.EV_KEY and event.value == 1:
        if event.code == 300: #up
            events.put(0.0)
        if event.code == 301: #right
            events.put(0.2)
        if event.code == 302: #down
            events.put(0.4)
        if event.code == 303: #left
            events.put(0.6)


def input_loop():
    for event in pad.read_loop():
        handle_event(event)

input_thread = Thread(target=input_loop)
input_thread.daemon = True
input_thread.start()

hue = 0
val = 0

while True:
    if not events.empty():
        hue = events.get_nowait()
        val = 1
    color = colorsys.hsv_to_rgb(hue, 1, val)
    pds.set_all(color)
    pds.update()
    val = val * 0.85
    if val <= 0.05:
        val = 0.0
    sleep(1.0/FRAMERATE)


