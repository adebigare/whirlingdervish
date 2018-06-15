#!/usr/bin/python

#also written by dlaw. see license in lights.py

import lights, colorsys, time

hue = 0
while True:
    hue = (hue + .1) % 1
    color = colorsys.hsv_to_rgb(hue, 1, 1)
#    lights.rgb.fill(0)
#    for i in range(50):
#       rgb[i] = color
#       lights.display(rgb)

    lights.set_all(color)
    lights.display()
    time.sleep(0.5)

    lights.clear()
    lights.display()
    time.sleep(0.5)
