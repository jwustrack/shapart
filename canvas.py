import numpy
import cairo
import math

c_format = cairo.FORMAT_RGB24

class Canvas(object):
    def __init__(self, offset, size, surface):
        self.x, self.y = offset
        self.w, self.h = size
        self.surface = surface
        buf = self.surface.get_data()
        self.data = numpy.ndarray(shape=(self.w, self.h, 4),
                                 dtype=numpy.uint8,
                                 buffer=buf)

    def sub(self, offset, size):
        subx, suby = offset
        subw, subh = size
        surface = self.surface.create_for_rectangle(subx, suby, subw, subh)
        return Canvas((self.x+subx, self.y+suby), (subw, subh), surface)

    def to_png(self, fobj):
        self.surface.write_to_png(fobj)

    def to_pil(self):
        from PIL import Image
        data_BGRa = numpy.array(self.surface.get_data()).reshape((self.w, self.h, 4))
        data_RGBa = data_BGRa[:, :, [2, 1, 0, 3]]
        return Image.frombytes('RGBa', (self.w, self.h), data_RGBa.flatten(), 'raw')

    def arc(self, x, y, s, r, g, b):
        s *= min(self.w, self.h)
        cr = cairo.Context(self.surface)
        cr.arc(self.w*x, self.h*y, s/2, 0, 2*math.pi)
        cr.set_source_rgb(r, g, b)
        cr.fill()

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
