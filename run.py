#!/usr/bin/python

#also written by dlaw. see license in lights.py

import numpy
import colorsys
from time import sleep
from lights import PowerSupply
from evdev import InputDevice, categorize, ecodes
from threading import Thread
from Queue import Queue

# Constants

FRAMERATE = 25.0
NUM_LIGHTS = 50
PAD_PATH = "/dev/input/by-id/usb-mayflash_limited_MAYFLASH_GameCube_Controller_Adapter-event-joystick"

# Animations

class Animation(object):
    def __init__(self):
        self.done = False

    def update(self, pixels):
        raise NotImplementedError

class Flash(Animation):
    def __init__(self, hue, offset=0, stride=1, decay=0.85):
        Animation.__init__(self)
        self._hue = hue
        self._offset = offset
        self._stride = stride
        self._decay = decay
        self._val = 1.0

    def update(self, pixels):
        view = pixels[self._offset::self._stride]
        color = colorsys.hsv_to_rgb(self._hue, 0.3, self._val)
        view += color
        self._val *= self._decay
        if self._val <= 0.01:
            self.done = True

class Seizure(Animation):
    def __init__(self, color, speed=4, dur=16):
        Animation.__init__(self)
        self._color = color
        self._speed = speed
        self._dur = dur
        self._iter = 0
        self._fct = 0

    def update(self, pixels):
        if self._iter >= self._dur:
            self.done = True
            return

        stride = self._iter % 2 
        pixels[0::2] = self._color if stride == 0 else (0,0,0) 
        pixels[1::2] = self._color if stride == 1 else (0,0,0)

        self._fct += 1
        if self._fct >= self._speed:
            self._fct = 0
            self._iter += 1

class Chaser(Animation):
    def __init__(self, hue, speed):
        Animation.__init__(self)
        self._hue = hue
        self._speed = speed
        self._fidx = 0.0
        self._dir = 1

    def update(self, pixels):
        tail = 8
        if self._idx >= NUM_LIGHTS - 1:
            self._dir = -1
        elif self._idx <= -tail and self._dir < 0:
            self.done = True 
            return

        for i in range(tail):
            idx = self._idx - (i * self._dir)
            if idx < 0 or idx >= NUM_LIGHTS:
                continue
            val = pow(0.6,i)
            color = colorsys.hsv_to_rgb(self._hue, 1.0, val)
            pixels[idx] = color

        self._fidx += self._speed * self._dir
        return

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
    for event in pad.read_loop():
        if event.type == ecodes.EV_KEY:
            inputs.put((event.code, event.value))

def process_inputs(inputs):
    animations = []

    up = inputs.get(Button.UP, False)
    down = inputs.get(Button.DOWN, False)
    left = inputs.get(Button.LEFT, False)
    right = inputs.get(Button.RIGHT, False)

    if up and down:
        animations.append(Flash(0.0)) 
    elif up:
        animations.append(Chaser(0.125, 0.66))
    elif down:
        animations.append(Chaser(0.8, 0.8))

    if left and right:
        animations.append(Flash(0.3))
    elif left:
        animations.append(Chaser(0.4, 1.0))
    elif right:
        animations.append(Chaser(0.6, 1.33))

    return animations

def render(pds, animations):
    pds.clear()
    for anim in animations:
        anim.update(pds.rgb)
    pds.update()

def main():
    pds = PowerSupply('192.168.0.101')
    input_thread = Thread(target=input_loop)
    input_thread.daemon = True
    input_thread.start()

    animations = []

    while True:
        # prune finished animations
        animations = [anim for anim in animations if not anim.done]

        # get current button events
        current_inputs = {}
        while not inputs.empty():
            (btn, val) = inputs.get_nowait()
            current_inputs[btn] = val

        # add any new animations based on button states
        new_animations = process_inputs(current_inputs)
        animations.extend(new_animations)

        # render the animations
        render(pds, animations)
        sleep(1.0/FRAMERATE)

if __name__== "__main__":
      main()
