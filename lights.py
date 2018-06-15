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

class PowerSupply(object):
    def __init__(self, address, port=6038, count=50):
        self._count = count
        self.rgb = numpy.zeros((count, 3), 'float')
        self._scaled = numpy.empty((count, 3), 'ubyte')
        self._xmit = numpy.zeros(533, 'ubyte')
        self._xmit[:8] = [4,1,220,74,1,0,1,1]
        self._xmit[15:21] = [0,255,255,255,255,0]
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
        self._sock.connect((address, port))

    def update(self):
        self._scaled = numpy.minimum(256 * numpy.maximum(self.rgb, 0), 255)
        self._send()

    def set_all(self, color):
        self.rgb[:] = color

    def set_pixel(self, index, color):
        self.rgb[index] = color

    def clear(self):
        self.rgb.fill(0)

    # single channel (0, xmit[11]) supported for now
    def _send(self):
        self._xmit[21:171] = numpy.ravel(self._scaled)
        self._sock.sendall(self._xmit)

