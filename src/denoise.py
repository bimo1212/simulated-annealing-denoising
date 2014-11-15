#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PIL import Image
from random import randint
from util import *

import numpy as np
import argparse
from scipy import ndimage


def prob(E1, E2, t):
    return 1 if E1 > E2 else np.exp((E1 - E2)/t)


def E_generator(beta, eta, h):
    def E(x, y):
        e1 = np.sum(np.multiply(x, y))
        weights = [[[0, 1, 0], [0, 0, 0], [0, 0, 0]],
                   [[0, 0, 0], [1, 0, 0], [0, 0, 0]],
                   [[0, 0, 0], [0, 0, 1], [0, 0, 0]],
                   [[0, 0, 0], [0, 0, 0], [0, 1, 0]]]
        neighbors = map(lambda w:
                        ndimage.filters.correlate(x, w, mode='constant'),
                        weights)
        e2m = reduce(lambda x, y: np.multiply(x, y), neighbors)
        e2 = np.sum(e2m)
        e3 = np.sum(x)
        print e2m
        print "%.4f, %.4f, %.4f" % (-e1, -e2, e3)
        return -beta * e1 -eta * e2 + h * e3
    return E


def temperature(k, kmax):
    return 1.0/500 * (1.0/k - 1.0/kmax)

name = {-1: 'BLACK', 1: 'WHITE'}

def simulated_annealing(y, kmax, E):
    x = np.array(y)
    Ebest = E(x, y)

    for k in range(1, kmax + 1):
        t = temperature(k, kmax)
        print "Temperature = %.4f" % (t)
        for idx in np.ndindex(y.shape):
            if idx[1] % x.shape[1] == 0:
                print "Line %d, Ebest = %.4f" % (idx[0], Ebest)
                result = sign(x, {-1: 0, 1: 255})
                Image.fromarray(result).convert('1').save('temp-%d.png' % (idx[0]))
            E1 = E(x, y)
            x[idx] *= -1
            E2 = E(x, y)
            print idx, "E1 = %.4f, E2 = %.4f" % (E1, E2)
            if prob(E1, E2, t) > randint(0, 1):
                print "Accept, x[", idx, "] = %s" % (name[x[idx]])
                if (E2 < Ebest):
                    Ebest = E2
            else:
                x[idx] *= -1  # flip back
                print "Reject, x[", idx, "] = %s" % (name[x[idx]])

    return x, Ebest


def denoise_image(image, args):
    data = sign(image.getdata(), {0: -1, 255: 1})
    E = E_generator(args.beta, args.eta, args.argh)
    result, _ = simulated_annealing(np.reshape(data, image.size[::-1]),
                                    args.kmax, E)
    result = sign(result, {-1: 0, 1: 255})
    return Image.fromarray(result).convert('1')


def main():
    args = get_args(src="flipped.png", dest="best.png")
    image = Image.open(args.input)
    result = denoise_image(image, args)
    result.save(args.output)

if __name__ == "__main__":
    main()