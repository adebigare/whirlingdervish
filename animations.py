import numpy
import colorsys

NUM_LIGHTS=50

class Animation(object):
    def __init__(self):
        self.done = False

    def update(self, pixels):
        raise NotImplementedError

class Flash(Animation):
    def __init__(self, hue, sat=0.3, offset=0, stride=1, decay=0.85):
        Animation.__init__(self)
        self._hue = hue
        self._sat = sat
        self._offset = offset
        self._stride = stride
        self._decay = decay
        self._val = 1.0

    def update(self, pixels):
        view = pixels[self._offset::self._stride]
        color = colorsys.hsv_to_rgb(self._hue, self._sat, self._val)
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
