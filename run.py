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

FRAMERATE = 30.0
NUM_LIGHTS = 50
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
        adjust = self._val
        self._val *= self._decay
        if self._val <= 0.01:
            self.done = True
        return pixels + adjust

class Chaser(Animation):
    def __init__(self, hue, speed):
        Animation.__init__(self)
        self._hue = hue
        self._speed = speed
        self._fidx = 0.0

    def update(self, pixels):
        if self._idx >= NUM_LIGHTS:
            self.done = True 
            return pixels

        for i in range(3):
            idx = self._idx - i
            if idx < 0:
                continue
            val = 1.0 - (i * 0.4)
            color = colorsys.hsv_to_rgb(self._hue, 1, val)
            pixels[idx] = color

        self._fidx += self._speed
        return pixels

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

    if up:
        animations.append(Chaser(0.0, 0.5))
    if down:
        animations.append(Chaser(0.2, 0.75))
    if left and right:
        animations.append(Flash())
    elif left:
        animations.append(Chaser(0.4, 1.0))
    elif right:
        animations.append(Chaser(0.6, 1.5))

    return animations

def render(pds, animations):
    pds.clear()
    rgb = pds.rgb
    for anim in animations:
        rgb = anim.update(rgb)
    pds.rgb = rgb
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
