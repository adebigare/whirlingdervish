#!/usr/bin/python

#also written by dlaw. see license in lights.py

import numpy
import colorsys
from time import sleep
from lights import PowerSupply
from animations import Chaser, Flash
from evdev import InputDevice, categorize, ecodes
from threading import Thread
from Queue import Queue

# Constants

PDS_IP = "192.168.1.100"
FRAMERATE = 30.0
PAD_PATH = "/dev/input/by-id/usb-mayflash_limited_MAYFLASH_GameCube_Controller_Adapter-event-joystick"

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
    pds = PowerSupply(PDS_IP)
    input_thread = Thread(target=input_loop)
    input_thread.daemon = True
    input_thread.start()

    frame_count = 0
    animations = [Flash(0.3, 0.7, decay=0.95)]

    while True:
        # prune finished animations
        animations = [anim for anim in animations if not anim.done]

        # get current button events every 3 frames
        # (gives leeway in "double press" states)
        if frame_count % 3 == 0:
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
        frame_count += 1

if __name__== "__main__":
      main()
