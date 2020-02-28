#!/usr/bin/env python
import pygame
import canvas
import sys
import evolve
from PIL import Image
from random import randint
from math import ceil
import numpy
import queue
import threading


class Broadcaster(object):

    def __init__(self, queues):
        self.queues = queues

    def put(self, msg):
        for q in self.queues:
            q.put(msg)

def draw(shapes_queue, c, block=True):
    screen.blit(c.to_pygame(), (0,0))
    pygame.display.update()
    i = 0
    x_min = None
    while True:
        try:
            x, y, s, r, g, b = shapes_queue.get(block=block)
        except queue.Empty:
            return
        x, y, w, h = c.arc(x, y, s, r, g, b)

def refresh(c):
    clock = pygame.time.Clock()
    while True:
        clock.tick_busy_loop(40)
        screen.blit(c.to_pygame(), (0,0))
        for s in old_selections:
            try:
                old_selections.remove(s)
                selections.remove(s)
            except ValueError:
                pass
            pygame.display.update(s)
        for s in selections:
            pygame.draw.rect(screen, (0, 255, 0), s, width=1)
            pygame.display.update(s)
        if curr_selection is not None:
            pygame.draw.rect(screen, (255, 0, 0), curr_selection, width=1)
            pygame.display.update(curr_selection)

selections = []
curr_selection = None
old_selections = []

def evolver(shapes_queue, origPIL, artPIL, scale):
    global curr_selection
    selections.append(curr_selection)
    evolver_rect = curr_selection
    curr_selection = None
    evolve.evolveBox(shapes_queue, origPIL, artPIL, evolver_rect.left/args.scale, evolver_rect.top/args.scale, evolver_rect.right/args.scale, evolver_rect.bottom/args.scale)
    old_selections.append(evolver_rect)

def instr_writer(f_queue, f_obj):
    while True:
        x, y, s, r, g, b = shapes_queue.get(block=True)
        f_obj.write(f'arc {x} {y} {s} {r} {g} {b}\n')
        f_obj.flush()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument("orig", type=argparse.FileType('rb'))
    parser.add_argument("width", type=int)
    parser.add_argument("height", type=int)
    parser.add_argument("scale", type=int)
    parser.add_argument("instructions", type=argparse.FileType('a+'))

    args = parser.parse_args()

    c = canvas.monochrome(args.width, args.height, (1, 1, 1))

    pygame.display.init()
    screen = pygame.display.set_mode((args.width, args.height), 0, 32)


    origPIL = Image.open(args.orig)
    origWidth, origHeight = origPIL.width, origPIL.height
    artPIL = Image.new(origPIL.mode, (origPIL.width, origPIL.height), (255, 255, 255))

    origPIL = origPIL.resize((ceil(args.width/args.scale), ceil(args.height/args.scale)))
    artPIL = artPIL.resize((ceil(args.width/args.scale), ceil(args.height/args.scale)))

    shapes_queue = queue.Queue()
    file_queue = queue.Queue()

    print('Bootstrapping')
    bsc = canvas.from_pil(artPIL)
    args.instructions.seek(0)
    for l in args.instructions:
        x, y, s, r, g, b = (float(_) for _ in l.split()[1:])
        bsc.arc(x, y, s, r, g, b)
        shapes_queue.put((x, y, s, r, g, b))
    draw(shapes_queue, c, False)
    pygame.display.update()
    print('Bootstrapping done')

    artPIL = bsc.to_pil()

    draw_thread = threading.Thread(target=lambda: draw(shapes_queue, c))
    draw_thread.start()

    refresh_thread = threading.Thread(target=lambda: refresh(c))
    refresh_thread.start()

    inst_writer_thread = threading.Thread(target=lambda: instr_writer(file_queue, args.instructions))
    inst_writer_thread.start()

    threads = []
    down_x, down_y = None, None

    while True:
      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          raise SystemExit
        if event.type == pygame.MOUSEBUTTONDOWN:
          down_x, down_y = pygame.mouse.get_pos()
        if event.type == pygame.MOUSEMOTION and down_x is not None:
          x, y = pygame.mouse.get_pos()
          if curr_selection is not None:
              old_selections.append(curr_selection)
          curr_selection = pygame.Rect((down_x, down_y), (x-down_x, y-down_y))
        if event.type == pygame.MOUSEBUTTONUP:
          x, y = pygame.mouse.get_pos()
          curr_selection = pygame.Rect((down_x, down_y), (x-down_x, y-down_y))

          evolve_thread = threading.Thread(target=lambda: evolver(Broadcaster([shapes_queue, file_queue]), origPIL, artPIL, args.scale))
          evolve_thread.start()
          threads.append(evolve_thread)
          down_x, down_y = None, None
          curr_selection = None
