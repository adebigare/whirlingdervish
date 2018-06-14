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
unscaled = numpy.empty((1, 50, 3), 'float')
scaled = numpy.empty((1, 50, 3), 'ubyte')
xmit = numpy.zeros(171, 'ubyte')
xmit[:8], xmit[15:21] = [4,1,220,74,1,0,1,1], [255,255,255,255,255, 255]
#xmit[:8], xmit[20:24] = [4,1,220,74,1,0,1,1], [255,255,255,255]
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
sock.connect(('192.168.0.101', 6038))

# internal utilities
def send(chan, data):
    xmit[11], xmit[21:] = chan, numpy.ravel(data)
    sock.sendall(xmit)
def scale(arr):
    return numpy.minimum(256 * numpy.maximum(arr, 0), 255)

# the public-facing function
def display(pixels):
    """
    pixels is broadcast to shape (10, 10, 3).
    Entries of pixels are floats between 0 and 1.
    """
    unscaled[:] = pixels
    #scaled[0::2] = scale(unscaled[0::2, ::-1])
    #scaled[1::2] = scale(unscaled[1::2])
    scaled = scale(unscaled)
    send(0, scaled)
    #send(2, scaled)
