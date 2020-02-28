#!/usr/bin/env python
import sys

import canvas

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("width", type=int)
    parser.add_argument("height", type=int)
    parser.add_argument("instructions", type=argparse.FileType('r'))
    parser.add_argument("img_out", type=argparse.FileType('wb'))
    args = parser.parse_args()

    c = canvas.monochrome(args.width, args.height, (1, 1, 1))
    for l in args.instructions:
        canvas.shape_from_str(l).draw(c)
    c.to_png(args.img_out)
