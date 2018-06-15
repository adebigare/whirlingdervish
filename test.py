#!/usr/bin/python

#also written by dlaw. see license in lights.py

import lights, colorsys, time

pds = lights.PowerSupply('192.168.0.101')

hue = 0
val = 0
while True:
    val = (val + .01) % 1
    color = colorsys.hsv_to_rgb(hue, 1, val)
    pds.set_all(color)
    pds.update()
    time.sleep(0.05)
