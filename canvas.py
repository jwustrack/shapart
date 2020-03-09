import math
from random import random, choice

import numpy
import cairo
from PIL import Image
import pygame

def rand(m, M):
    return m + random()*(M-m)

def shape_from_str(s):
    '''
    >>> shape_from_str('disc 0.5 0.4 0.1 0.5 0.6 0.7')
    Disc((0.5, 0.4), 0.1, (0.5, 0.6, 0.7))
    >>> shape_from_str('rect 0.2 0.4 0.1 0.3 0.4 0.5 0.6')
    Rect((0.2, 0.4), (0.1, 0.3), (0.4, 0.5, 0.6))
    '''
    shape, args = s.split(' ', 1)
    args = args.split()
    return {
        "disc": Disc,
        "rect": Rect,
        "line": Line,
    }[shape].from_str(args)

class Disc(object):

    def __init__(self, pos, size, color):
        self.pos = pos
        self.size = size
        self.color = color

    def draw(self, canvas):
        size = self.size * min(canvas.w, canvas.h)
        cr = canvas.context()
        x, y = self.pos
        cr.arc(canvas.w*x, canvas.h*y, size/2, 0, 2*math.pi)
        cr.set_source_rgb(*self.color)
        cr.fill()

    def scale(self, crop_w, crop_h, offset_x, offset_y, full_w, full_h):
        x, y = self.pos
        x = (x * crop_w + offset_x) / full_w
        y = (y * crop_h + offset_y) / full_h
        self.pos = x, y
        self.size *= min(crop_w, crop_h) / min(full_w, full_h)

    @staticmethod
    def from_str(args):
        x, y, size, r, g, b = (float(_) for _ in args)
        return Disc((x, y), size, (r, g, b))

    @staticmethod
    def rand():
        size = rand(.01, .40)
        x, y = rand(size/2, 1-size/2), rand(size/2, 1-size/2)
        r, g, b = random(), random(), random()
        return Disc((x, y), size, (r, g, b))

    def __repr__(self):
        return f'Disc({self.pos}, {self.size}, {self.color})'

    def __str__(self):
        '''
        >>> disc = Disc((1, 2), 3, (.4, .5, .6))
        >>> f'{disc}'
        'disc 1 2 3 0.4 0.5 0.6'
        '''
        x, y = self.pos
        r, g, b = self.color
        return f'disc {x} {y} {self.size} {r} {g} {b}'

class Line(object):

    def __init__(self, pos1, pos2, width, color):
        self.pos1 = pos1
        self.pos2 = pos2
        self.width = width
        self.color = color

    @staticmethod
    def from_str(args):
        x1, y1, x2, y2, w, r, g, b = (float(_) for _ in args)
        return Line((x1, y1), (x2, y2), w, (r, g, b))

    @staticmethod
    def rand():
        w, h = rand(.01, .4), rand(.01, .4)
        x, y = rand(0, 1-w), rand(0, 1-h)
        width = rand(0.001, .01)
        #r, g, b = random(), random(), random()
        r, g, b = choice([
            (28, 99, 125),
            (24, 178, 186),
            (211, 236, 238),
            (170, 70, 70),
            #            (70, 170, 70),
            #            (70, 70, 170),
            (20, 20, 20),
            (0, 0, 0),
            (255, 255, 255),
            (217, 162, 150),
            ])
        r /= 255.0
        g /= 255.0
        b /= 255.0
        #r = g = b = random()
        return Line((x, y), (x+w, x+h), width, (r, g, b))

    def scale(self, crop_w, crop_h, offset_x, offset_y, full_w, full_h):
        x, y = self.pos1
        x = (x * crop_w + offset_x) / full_w
        y = (y * crop_h + offset_y) / full_h
        self.pos1 = x, y

        x, y = self.pos2
        x = (x * crop_w + offset_x) / full_w
        y = (y * crop_h + offset_y) / full_h
        self.pos2 = x, y

        self.width *= crop_w / full_w

    def draw(self, canvas):
        cr = canvas.context()
        x1, y1 = self.pos1
        x2, y2 = self.pos2
        cr.set_source_rgb(*self.color)
        cr.set_line_width(canvas.w*self.width)
        cr.move_to(canvas.w*x1, canvas.h*y1)
        cr.line_to(canvas.w*x2, canvas.h*y2)
        cr.stroke()

    def __repr__(self):
        return f'Line({self.pos1}, {self.pos2}, {self.width}, {self.color})'

    def __str__(self):
        x1, y1 = self.pos1
        x2, y2 = self.pos2
        r, g, b = self.color
        return f'line {x1} {y1} {x2} {y2} {self.width} {r} {g} {b}'

class Rect(object):

    def __init__(self, pos, size, color):
        self.pos = pos
        self.size = size
        self.color = color

    @staticmethod
    def from_str(args):
        x, y, w, h, r, g, b = (float(_) for _ in args)
        return Rect((x, y), (w, h), (r, g, b))

    @staticmethod
    def rand():
        w, h = rand(.01, .40), rand(.01, .40)
        x, y = rand(0, 1-w), rand(0, 1-h)
        r, g, b = random(), random(), random()
        return Rect((x, y), (w, h), (r, g, b))

    def scale(self, crop_w, crop_h, offset_x, offset_y, full_w, full_h):
        x, y = self.pos
        x = (x * crop_w + offset_x) / full_w
        y = (y * crop_h + offset_y) / full_h
        self.pos = x, y
        w, h = self.size
        w *= crop_w / full_w
        h *= crop_h / full_h
        self.size = w, h

    def draw(self, canvas):
        cr = canvas.context()
        x, y = self.pos
        w, h = self.size
        cr.rectangle(canvas.w*x, canvas.h*y, w*canvas.w, h*canvas.h)
        cr.set_source_rgb(*self.color)
        cr.fill()

    def __repr__(self):
        return f'Rect({self.pos}, {self.size}, {self.color})'

    def __str__(self):
        x, y = self.pos
        r, g, b = self.color
        w, h = self.size
        return f'rect {x} {y} {w} {h} {r} {g} {b}'

c_format = cairo.FORMAT_RGB24

def bgra_surf_to_rgba_string(cairo_surface):
    # We use PIL to do this
    img = Image.frombuffer(
        'RGBA', (cairo_surface.get_width(),
                 cairo_surface.get_height()),
        bytes(cairo_surface.get_data()), 'raw', 'BGRA', 0, 1)
    return img.tobytes('raw', 'RGBA', 0, 1)

class Canvas(object):
    def __init__(self, offset, size, surface):
        self.x, self.y = offset
        self.w, self.h = size
        self.surface = surface
        buf = self.surface.get_data()
        self.data = numpy.ndarray(shape=(self.w, self.h, 4),
                                  dtype=numpy.uint8,
                                  buffer=buf)

    def context(self):
        return cairo.Context(self.surface)

    def sub(self, offset, size):
        subx, suby = offset
        subw, subh = size
        surface = self.surface.create_for_rectangle(subx, suby, subw, subh)
        return Canvas((self.x+subx, self.y+suby), (subw, subh), surface)

    def to_png(self, fobj):
        self.surface.write_to_png(fobj)

    def to_pil(self):
        data_BGRa = numpy.array(self.surface.get_data()).reshape((self.w, self.h, 4))
        data_RGBa = data_BGRa[:, :, [2, 1, 0, 3]]
        return Image.frombytes('RGBa', (self.w, self.h), data_RGBa.flatten(), 'raw')

    def to_pygame(self):
        data_string = bgra_surf_to_rgba_string(self.surface)
        return pygame.image.frombuffer(data_string, (self.w, self.h), 'RGBA')

    def copy(self):
        new_data = self.data.copy()
        surface = cairo.ImageSurface.create_for_data(new_data, c_format, self.w, self.h)
        return Canvas((self.x, self.y), (self.w, self.h), surface)

def from_png(fobj):
    surface = cairo.ImageSurface.create_from_png(fobj)
    w, h = surface.get_width(), surface.get_height()
    return Canvas((0, 0), (w, h), surface)

def from_pil(im, alpha=1.0, format=cairo.FORMAT_RGB24):
    assert format in (cairo.FORMAT_RGB24, cairo.FORMAT_ARGB32), "Unsupported pixel format: %s" % format
    if 'A' not in im.getbands():
        im.putalpha(int(alpha * 256.))
    arr = bytearray(im.tobytes('raw', 'BGRa'))
    surface = cairo.ImageSurface.create_for_data(arr, format, im.width, im.height)
    return Canvas((0, 0), (im.width, im.height), surface)

def monochrome(w, h, color):
    surface = cairo.ImageSurface(c_format, w, h)
    cr = cairo.Context(surface)
    cr.set_source_rgb(*color)
    cr.paint()
    return Canvas((0, 0), (w, h), surface)
