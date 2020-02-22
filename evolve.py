import numpy
import sys
import os.path
import canvas
from random import random

def rand(m, M):
    return m + random()*(M-m)

def rand_draw_params():
    s = rand(.01, .40)
    x, y = rand(s/2, 1-s/2), rand(s/2, 1-s/2)
    r, g, b = random(), random(), random()
    return x, y, s, r, g, b

def mse(A, B):
    return ((numpy.array(A, dtype=numpy.int32) - B)**2).mean(axis=None)

def scale(x, y, s, w, h, offset_x, offset_y, full_w, full_h):
    new_x = (x * w + offset_x) / full_w
    new_y = (y * h + offset_y) / full_h
    new_s = s * min(w, h) / min(full_w, full_h)
    return new_x, new_y, new_s


def evolve(orig, art, offset_x, offset_y, full_w, full_h, steps=1):
    loss = mse(orig.data, art.data)
    for _ in range(steps):
        new_art = art.copy()
        x, y, s, r, g, b = rand_draw_params()
        new_art.arc(x, y, s, r, g, b)
        new_loss = mse(orig.data, new_art.data)
        if new_loss < loss:
            art, loss = new_art, new_loss
            sx, sy, ss = scale(x, y, s, orig.w, orig.h, offset_x, offset_y, full_w, full_h)
            print("{0} {1}".format(loss, ' '.join(str(_) for _ in (sx, sy, ss, r, g, b))))
    return art


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("img_in")
    parser.add_argument("img_out")
    args = parser.parse_args()

    d = canvas.load(args.img_in)
    w, h, _ = d.shape

    if os.path.isfile(args.img_out):
        d1 = canvas.load(args.img_out)
    else:
        d1 = canvas.blank(w, h)

    i = 0
    e1 = mse(d, d1)
    while True:
        for _ in range(1000):
            i += 1
            d2 = d1.copy()
            x, y, s, r, g, b = rand_draw_params(w, h)
            canvas.arc(d2, w, h, x, y, s, r, g, b)
            e2 = mse(d, d2)
            if e2 < e1:
                d1 = d2
                e1 = e2
                print("{0} {1}".format(e1, ' '.join(str(_) for _ in (x, y, s, r, g, b))))
                print(f'{i}: {e2}', end='\r', file=sys.stderr)

        canvas.save(args.img_out, d1, w, h)
