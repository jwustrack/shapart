import sys
import os.path
from random import random

import numpy

import canvas

def mse(A, B):
    return ((numpy.array(A, dtype=numpy.int32) - B)**2).mean(axis=None)

def randStd(low, high):
    mean = (low+high)/2
    dev = (high-low)/6
    x = numpy.random.normal(mean, dev)
    return round(max(min(x, high), low))

def randStdCrop(left, top, right, bottom, crop_w, crop_h):
    rand_x = randStd(left, right - crop_w)
    rand_y = randStd(top, bottom - crop_h)
    return rand_x, rand_y, rand_x+crop_w, rand_y+crop_h

def evolveCrop(shapes_queue, orig_pil, art_pil, steps, left, top, right, bottom):
    orig = canvas.from_pil(orig_pil.crop((left, top, right, bottom)))
    art = canvas.from_pil(art_pil.crop((left, top, right, bottom)))
    art = evolve(shapes_queue, orig, art, offset_x=left, offset_y=top, full_w=orig_pil.width, full_h=orig_pil.height, steps=steps)
    art_pil.paste(art.to_pil(), (left, top))

def evolveBox(shapes_queue, orig_pil, art_pil, left, top, right, bottom):
    for _ in range(1000):
        crop = randStdCrop(left, top, right, bottom, 10, 10)
        evolveCrop(shapes_queue, orig_pil, art_pil, 10, *crop)

def evolve(shapes_queue, orig, art, offset_x, offset_y, full_w, full_h, steps=1):
    loss = mse(orig.data, art.data)
    for _ in range(steps):
        new_art = art.copy()
        disc = canvas.Rect.rand()
        disc.draw(new_art)
        new_loss = mse(orig.data, new_art.data)
        if new_loss < loss:
            art, loss = new_art, new_loss
            disc.scale(orig.w, orig.h, offset_x, offset_y, full_w, full_h)
            shapes_queue.put(disc)
    return art
