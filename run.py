import evolve
from PIL import Image
from random import randint
from math import ceil
import numpy

subscale = 1

origPIL = Image.open('spgr/orig.jpg')
origWidth, origHeight = origPIL.width, origPIL.height
artPIL = Image.open('spgr/artpil.png')
#artPIL = Image.new(origPIL.mode, (origPIL.width, origPIL.height), (255, 255, 255))

origPIL = origPIL.resize((ceil(origWidth/subscale), ceil(origHeight/subscale)))
artPIL = artPIL.resize((ceil(origWidth/subscale), ceil(origHeight/subscale)))
#artPIL = Image.open('snow/artpil.png')#Image.new(origPIL.mode, (origPIL.width, origPIL.height), (255, 255, 255))

def randCrop(x, y, x_to, y_to, crop_w, crop_h):
    rand_x = randint(x, x_to - crop_w)
    rand_y = randint(y, y_to - crop_h)
    return rand_x, rand_y, rand_x+crop_w, rand_y+crop_h

def randStd(low, high):
    mean = (low+high)/2
    dev = (high-low)/6
    x = numpy.random.normal(mean, dev)
    return round(max(min(x, high), low))

def randStdCrop(x, y, x_to, y_to, crop_w, crop_h):
    rand_x = randStd(x, x_to - crop_w)
    rand_y = randStd(y, y_to - crop_h)
    return rand_x, rand_y, rand_x+crop_w, rand_y+crop_h

def evolveCrop(origPIL, artPIL, steps, x, y, x_to, y_to):
    orig = evolve.canvas.from_pil(origPIL.crop((x, y, x_to, y_to)))
    art = evolve.canvas.from_pil(artPIL.crop((x, y, x_to, y_to)))
    art = evolve.evolve(orig, art, offset_x=x, offset_y=y, full_w=origPIL.width, full_h=origPIL.height, steps=steps)
    artPIL.paste(art.to_pil(), (x, y))

def evolveAll():
    for _ in range(20000):
        crop = randStdCrop(0, 0, origPIL.width, origPIL.height, 10, 10)
        evolveCrop(origPIL, artPIL, 10, *crop)

def evolveBox(x, y, x_to, y_to):
    for _ in range(2000):
        crop = randStdCrop(x, y, x_to, y_to, 10, 10)
        evolveCrop(origPIL, artPIL, 100, *crop)

#evolveAll()
#evolveBox(188, 25, 712, 428)
#evolveBox(682, 25, 1080, 400)
evolveBox(347, 460, 510, 730)
#evolveBox(366, 139, 531, 300)
#evolveBox(819, 124, 923, 244)
#evolveBox(270, 44, 567, 359)
#evolveBox(760, 34, 962, 294)

artPIL.resize((origWidth, origHeight)).save("spgr/artpil.png")
