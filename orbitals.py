#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os.path
import cairo
from PIL import Image
import numpy as np
from numpy import (sin, cos, pi, arctan2, square, sqrt, logical_not, linspace,
                array, zeros)
from numpy.random import random, randint, shuffle
from time import time

#np.random.seed(1)

COLOR_PATH = 'color/rgb.gif'
PI = pi
TWOPI = pi * 2.
SIZE = 10000 # size of png image
NUMBER_OF_NODES = 400 # number of nodes
MAXFS = 6 # max friendships pr node
BACK = 1. # background color
GRAINS = 30
ALPHA = 0.05 # opacity of drawn points
#STEPS = 10**7
STEPS = 10**7

PIXEL = 1. / SIZE

#STP = 0.0001 # scale motion in each iteration by this
STP = PIXEL/15.
RADIUS = 0.20 # radius of starting circle
FARL    = 0.15 # ignore "enemies" beyond this radius
NEARL = 0.01 # do not attempt to approach friends close than this

#UPDATE_NUMBER_OF_NODES = 2000
UPDATE_NUMBER_OF_NODES = 1000
FRIENDSHIP_RATIO = 0.1 # probability of friendship dens
FRIENDSHIP_INITIATE_PROB = 0.03 # probability of friendship initation attempt

FILENAME = 'res_c_num{:d}_fs{:d}_near{:2.4f}_far{:2.4f}_pa{:2.4f}_pb{:2.4f}'\
                     .format(NUMBER_OF_NODES, MAXFS, NEARL, FARL, \
                                     FRIENDSHIP_RATIO, FRIENDSHIP_INITIATE_PROB)
FILENAME = FILENAME + '_itt{:05d}.png'

print('SIZE', SIZE)
print('NUMBER_OF_NODES', NUMBER_OF_NODES)
print('STP', STP)
print('PIXEL', PIXEL)
print('MAXFS', MAXFS)
print('GRAINS', GRAINS)
print('COLOR_PATH', COLOR_PATH)
print('RADIUS', RADIUS)
print('FRIENDSHIP_RATIO', FRIENDSHIP_RATIO)
print('FRIENDSHIP_INITIATE_PROB', FRIENDSHIP_INITIATE_PROB)

class Render(object):
    def __init__(self):
        self.__init_cairo()
        self.__get_colors(COLOR_PATH)

    def __init_cairo(self):
        sur = cairo.ImageSurface(cairo.FORMAT_ARGB32, SIZE, SIZE)
        ctx = cairo.Context(sur)
        ctx.scale(SIZE, SIZE)
        ctx.set_source_rgb(BACK, BACK, BACK)
        ctx.rectangle(0, 0, 1, 1)
        ctx.fill()

        self.sur = sur
        self.ctx = ctx

    def __get_colors(self, f):
        if os.path.exists(f):
            scale = 1. / 255.
            im = Image.open(f)
            w, h = im.size
            rgbim = im.convert('RGB')
            res = []
            for i in range(0, w):
                for j in range(0, h):
                    r, g, b = rgbim.getpixel((i, j))
                    res.append((r * scale, g * scale, b * scale))

            shuffle(res)
            self.colors = res
            self.n_colors = len(res)
            print('Got %d colors from file %s' % (self.n_colors, f))
        else:
            print('Default color: black')
            self.colors = [(0, 0, 0)]
            self.n_colors = 1

    def connections(self, X, Y, F, A, R):
        """
        """
        indsx, indsy = F.nonzero()
        mask = indsx >= indsy

        for i, j in zip(indsx[mask], indsy[mask]):
            a = A[i, j]
            d = R[i, j]
            scales = random(GRAINS) * d
            xp = X[i] - scales * cos(a)
            yp = Y[i] - scales * sin(a)

            bla = (i * NUMBER_OF_NODES + j)
            colorIndex = bla % self.n_colors
            r, g, b = self.colors[colorIndex]
            self.ctx.set_source_rgba(r, g, b, ALPHA)

            for x, y in zip(xp, yp):
                self.ctx.rectangle(x, y, PIXEL, PIXEL)
                self.ctx.fill()

def set_distances(X, Y, A, R):

    for i in range(NUMBER_OF_NODES):

        dx = X[i] - X
        dy = Y[i] - Y
        R[i, :] = square(dx)+square(dy)
        A[i, :] = arctan2(dy, dx)

    sqrt(R, R)

def make_friends(i, F, R):
    cand_num = F.sum(axis=1)

    if cand_num[i]>=MAXFS:
        return

    cand_mask = cand_num<MAXFS
    cand_mask[i] = False
    cand_ind = cand_mask.nonzero()[0]

    cand_dist = R[i, cand_ind].flatten()
    cand_sorted_dist = cand_dist.argsort()
    cand_ind = cand_ind[cand_sorted_dist]

    cand_n = len(cand_ind)

    if cand_n<1:
        return

    for k in range(cand_n):

        if random()<FRIENDSHIP_RATIO:

            j = cand_ind[k]
            F[[i, j], [j, i]] = True
            return

def main():
    X = zeros(NUMBER_OF_NODES, 'float')
    Y = zeros(NUMBER_OF_NODES, 'float')
    SX = zeros(NUMBER_OF_NODES, 'float')
    SY = zeros(NUMBER_OF_NODES, 'float')
    R = zeros((NUMBER_OF_NODES, NUMBER_OF_NODES), 'float')
    A = zeros((NUMBER_OF_NODES, NUMBER_OF_NODES), 'float')
    F = zeros((NUMBER_OF_NODES, NUMBER_OF_NODES), 'byte')
    render = Render()

    if not os.path.exists('output'):
        os.mkdir('output')

    # Initial values
    for i in range(NUMBER_OF_NODES):
        the = random() * TWOPI
        x = RADIUS * sin(the)
        y = RADIUS * cos(the)
        X[i] = 0.5 + x
        Y[i] = 0.5 + y

    t_cum = 0.

    for itt in range(STEPS):
        set_distances(X, Y, A, R)
        SX[:] = 0.
        SY[:] = 0.
        t = time()

        for i in range(NUMBER_OF_NODES):
            xF = logical_not(F[i, :])
            d = R[i, :]
            a = A[i, :]
            near = d > NEARL
            near[xF] = False
            far = d < FARL
            far[near] = False
            near[i] = False
            far[i] = False
            speed = FARL - d[far]
            SX[near] += cos(a[near])
            SY[near] += sin(a[near])
            SX[far] -= speed * cos(a[far])
            SY[far] -= speed * sin(a[far])

        X += SX * STP
        Y += SY * STP

        if not (itt + 1) % 100:
            print(itt, sqrt(square(SX)+square(SY)).max())

        if random() < FRIENDSHIP_INITIATE_PROB:
            k = randint(NUMBER_OF_NODES)
            make_friends(k, F, R)

        render.connections(X, Y, F, A, R)
        t_cum += time() - t

        if not (itt + 1) % UPDATE_NUMBER_OF_NODES:
            fn = FILENAME.format(itt + 1)
            print(fn, t_cum)
            path = 'output/%s' % fn
            render.sur.write_to_png(path)
            t_cum = 0.

if __name__ == '__main__' :
    main()
