import numpy
import sys
import os.path
import canvas
from random import random as rand

def rand_draw_params(w, h):
    s = rand()
    x, y = rand(), rand()
    r, g, b = rand(), rand(), rand()
    return x, y, s, r, g, b

def mse(A, B):
    return ((numpy.array(A, dtype=numpy.int32) - B)**2).mean(axis=None)

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
