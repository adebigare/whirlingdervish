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

class Animation(object):
    def __init__(self):
        self.done = False

    def update(self, pixels):
        raise NotImplementedError

class Flash(Animation):
    def __init__(self, decay=0.85):
        Animation.__init__(self)
        self._decay = 0.85
        self._val = 1.0

    def update(self, pixels):
        pixels[:] = self._val
        self._val *= self._decay
        if self._val <= 0.01:
            self.done = True

class Chaser(Animation):
    def __init__(self, hue, speed):
        Animation.__init__(self)
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

class Button:
    UP = 300
    RIGHT = 301
    DOWN = 302
    LEFT = 303

def input_loop():
    pad = InputDevice(PAD_PATH)
    states = {
        Button.UP: False, Button.RIGHT: False,
        Button.DOWN: False, Button.LEFT : False
        }
    for event in pad.read_loop():
        if event.type == ecodes.EV_KEY:
            on = event.value == 1
            if event.code == Button.UP:
                states[Button.UP] = on
                if on:
                    inputs.put(Chaser(0.0, 0.75))
            if event.code == Button.RIGHT:
                states[Button.RIGHT] = on
                if on:
                    if states[Button.LEFT]:
                        inputs.put(Flash())
                    else:
                        inputs.put(Chaser(0.2, 0.5))
            if event.code == Button.DOWN:
                states[Button.DOWN] = on
                if on:
                    inputs.put(Chaser(0.4, 1.0))
            if event.code == Button.LEFT:
                states[Button.LEFT] = on
                if on:
                    if states[Button.RIGHT]:
                        inputs.put(Flash())
                    else:
                        inputs.put(Chaser(0.6, 1.5))

def main():
    pds = PowerSupply('192.168.0.101')
    input_thread = Thread(target=input_loop)
    input_thread.daemon = True
    input_thread.start()

    animations = []

    while True:
        if not inputs.empty():
            animations.append(inputs.get_nowait())
        pds.clear()
        for anim in animations:
            anim.update(pds.rgb)
        animations = [anim for anim in animations if not anim.done]
        pds.update()
        sleep(1.0/FRAMERATE)

if __name__== "__main__":
      main()
