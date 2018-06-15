# Copyright (C) 2012 David Lawrence
# 
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
# 
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
# 
#
# Modified 6-13-2018

import numpy, socket

# initialization
unscaled = numpy.zeros((50, 3), 'float')
scaled = numpy.empty((50, 3), 'ubyte')
xmit = numpy.zeros(533, 'ubyte')
xmit[:8], xmit[15:21] = [4,1,220,74,1,0,1,1], [0,255,255,255,255,0]
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
sock.connect(('192.168.0.101', 6038))

# internal utilities
def _send(chan, data):
    xmit[11], xmit[21:171] = chan, numpy.ravel(data)
    sock.sendall(xmit)

def _scale(arr):
    return numpy.minimum(256 * numpy.maximum(arr, 0), 255)

# the public-facing function

def display():
    scaled = _scale(unscaled)
    _send(0, scaled)

def set_all(color):
    unscaled[:] = color

def set_pixel(index, color):
    unscaled[index] = color

def clear():
    unscaled.fill(0)

