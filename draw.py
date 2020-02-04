import canvas
import sys

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("width", type=int)
    parser.add_argument("height", type=int)
    parser.add_argument("instructions", type=argparse.FileType('r'))
    parser.add_argument("img_out", type=argparse.FileType('wb'))
    args = parser.parse_args()

    data = canvas.blank(args.width, args.height)
    for l in open(sys.argv[3]):
        _, x, y, s, r, g, b = (float(_) for _ in l.split())
        canvas.arc(data, args.width, args.height, x, y, s, r, g, b)
    canvas.save(args.img_out, data, args.width, args.height)
