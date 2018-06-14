#!/usr/bin/python

#also written by dlaw. see license in lights.py

import lights, colorsys, time

hue = 0
while True:
    hue = (hue + .004) % 1
    color = colorsys.hsv_to_rgb(hue, 1, 1)
    lights.display(color)
    time.sleep(.03)
