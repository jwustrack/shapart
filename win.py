#!/usr/bin/env python
import sys
import queue
import threading
from random import randint
from math import ceil

import pygame
from PIL import Image

import evolve
import canvas

def points_to_rect(point1, point2):
    '''
    >>> points_to_rect((5, 2), (4, 3))
    <rect(4, 2, 1, 1)>
    >>> points_to_rect((10, 9), (3, 7))
    <rect(3, 7, 7, 2)>
    '''
    x1, y1 = point1
    x2, y2 = point2
    left, top = min(x1, x2), min(y1, y2)
    right, bottom = max(x1, x2), max(y1, y2)
    return pygame.Rect(left, top, right-left, bottom-top)

class Broadcaster(object):
    def __init__(self, queues):
        self.queues = queues

    def put(self, msg):
        for q in self.queues:
            q.put(msg)

def draw(shapes_queue, c, block=True):
    screen.blit(c.to_pygame(), (0,0))
    pygame.display.update()
    while True:
        try:
            shape = shapes_queue.get(block=block)
        except queue.Empty:
            return
        shape.draw(c)

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

def evolver(shapes_queue, orig_pil, art_pil, scale):
    global curr_selection
    selections.append(curr_selection)
    evolver_rect = curr_selection
    curr_selection = None
    evolve.evolveBox(shapes_queue, orig_pil, art_pil, evolver_rect.left/args.scale, evolver_rect.top/args.scale, evolver_rect.right/args.scale, evolver_rect.bottom/args.scale)
    old_selections.append(evolver_rect)

def instr_writer(f_queue, f_obj):
    while True:
        shape = shapes_queue.get(block=True)
        f_obj.write(f'{shape}\n')
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

    orig_pil = Image.open(args.orig)
    orig_pil = orig_pil.resize((ceil(args.width/args.scale), ceil(args.height/args.scale)))

    shapes_queue = queue.Queue()
    file_queue = queue.Queue()

    print('Loading shapes...')
    art = canvas.monochrome(orig_pil.width, orig_pil.height, (255, 255, 255))
    args.instructions.seek(0)
    for l in args.instructions:
        shapes_queue.put(canvas.shape_from_str(l))
    draw(shapes_queue, c, False)
    pygame.display.update()
    print('Done')

    art_pil = art.to_pil()

    draw_thread = threading.Thread(target=lambda: draw(shapes_queue, c))
    draw_thread.start()

    refresh_thread = threading.Thread(target=lambda: refresh(c))
    refresh_thread.start()

    inst_writer_thread = threading.Thread(target=lambda: instr_writer(file_queue, args.instructions))
    inst_writer_thread.start()

    threads = []
    selection_start = None

    while True:
      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          raise SystemExit

        elif event.type == pygame.MOUSEBUTTONDOWN:
          selection_start = pygame.mouse.get_pos()

        elif event.type == pygame.MOUSEMOTION and selection_start is not None:
          if curr_selection is not None:
              old_selections.append(curr_selection)
          curr_selection = points_to_rect(selection_start, pygame.mouse.get_pos())

        elif event.type == pygame.MOUSEBUTTONUP:
          curr_selection = points_to_rect(selection_start, pygame.mouse.get_pos())

          evolve_thread = threading.Thread(target=lambda: evolver(Broadcaster([shapes_queue, file_queue]), orig_pil, art_pil, args.scale))
          evolve_thread.start()
          threads.append(evolve_thread)

          selection_start = None
          curr_selection = None
