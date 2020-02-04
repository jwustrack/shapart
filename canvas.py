import numpy
import cairo
import math

c_format = cairo.FORMAT_RGB24

def load(fname) :
    surface = cairo.ImageSurface.create_from_png(fname)
    buf = surface.get_data()
    w, h = surface.get_width(), surface.get_height()
    return numpy.ndarray(shape=(w, h, 4),
                         dtype=numpy.uint8,
                         buffer=buf)

def blank(w, h):
    data = numpy.zeros((w, h, 4), dtype=numpy.uint8)
    surface = cairo.ImageSurface.create_for_data(data, c_format, w, h)
    cr = cairo.Context(surface)
    cr.set_source_rgb(1.0, 1.0, 1.0)
    cr.paint()
    return data

def save(fobj, data, w, h):
    surface = cairo.ImageSurface.create_for_data(data, c_format, w, h)
    surface.write_to_png(fobj)

def arc(data, w, h, x, y, s, r, g, b):
    s = s*w/100
    surface = cairo.ImageSurface.create_for_data(data, c_format, w, h)
    cr = cairo.Context(surface)
    cr.arc(w*x, h*y, s, 0, 2*math.pi)
    cr.set_line_width(s*2)
    cr.set_source_rgb(r, g, b)
    cr.stroke()
    surface.flush()
