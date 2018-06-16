#!/usr/bin/python

#also written by dlaw. see license in lights.py

import colorsys
from time import sleep
from lights import PowerSupply
from evdev import InputDevice, categorize, ecodes
from threading import Thread
from Queue import Queue

# Constants

FRAMERATE = 30.0
PAD_PATH = "/dev/input/by-id/usb-mayflash_limited_MAYFLASH_GameCube_Controller_Adapter-event-joystick"

# Animations

class Chaser(object):
    def __init__(self, hue, speed):
        self.done = False
        self._hue = hue
        self._speed = speed
        self._fidx = 0.0

    def update(self, pixels):
        for i in range(3):
            idx = self._idx - i
            if idx < 0:
                continue
            val = 1.0 - (i * 0.4)
            color = colorsys.hsv_to_rgb(self._hue, 1, val)
            pixels[idx] = color
        self._fidx += self._speed
        if self._idx >= 50:
            self.done = True 

    @property
    def _idx(self):
        return int(self._fidx)

# Input

inputs = Queue()

def handle_event(event):
    if event.type == ecodes.EV_KEY and event.value == 1:
        if event.code == 300: #up
            inputs.put((0.0, 0.6))
        if event.code == 301: #right
            inputs.put((0.2, 0.3))
        if event.code == 302: #down
            inputs.put((0.4, 1.0))
        if event.code == 303: #left
            inputs.put((0.6, 1.5))

def input_loop():
    pad = InputDevice(PAD_PATH)
    for event in pad.read_loop():
        handle_event(event)

def main():
    pds = PowerSupply('192.168.0.101')
    input_thread = Thread(target=input_loop)
    input_thread.daemon = True
    input_thread.start()

    chasers = [] 

    while True:
        if not inputs.empty():
            (hue, speed) = inputs.get_nowait() 
            chasers.append(Chaser(hue, speed))
        pds.clear()
        for chaser in chasers:
            chaser.update(pds.rgb)
        chasers = [chaser for chaser in chasers if not chaser.done]
        pds.update()
        sleep(1.0/FRAMERATE)

if __name__== "__main__":
      main()
