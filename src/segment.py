#!/usr/bin/env python

# MIT License

# Copyright (c) 2022 Simon Crase

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from abc               import ABC, abstractmethod
from argparse          import ArgumentParser
from loader            import Loader
from matplotlib.pyplot import close, figure, show
from numpy             import all, any, flip

class Segmenter(ABC):
    Segmenters = {}

    @classmethod
    def Register(cls,key,segmenter):
        Segmenter.Segmenters[key] = segmenter

    @classmethod
    def Create(cls,view):
        if view in Segmenter.Segmenters:
            return Segmenter.Segmenters[view]

    @abstractmethod
    def segment(self,pixels,laterality='L'):
        ...

class CranioCaudalSegmenter(Segmenter):
    def __init__(self):
        pass

    def segment(self,pixels,laterality='L'):
        pixels = self.standardize_orientation(pixels,axis=1)
        m0,n0,m1,n1 = segmenter.get_bounds(pixels)
        return pixels [m0:m1,n0:n1]

    def standardize_orientation(self,pixels,laterality='L'):
        if laterality=='R':
            pixels = flip(pixels,axis=1)
        return pixels

    def get_bounds(self,pixels,epsilon=0.01):
        threshold = pixels.max() - epsilon
        m,n       = pixels.shape
        m0,n0     = 0,0
        n1        = 1
        m1        = m-1

        while n1<n:
            if all(pixels[: ,n1]>threshold):
                break
            n1 += 1
        while m0<m:
            if any(pixels[m0,n0:n1]<threshold):
                break
            m0 += 1
        while m1>m0:
            if any(pixels[m1,n0:n1]<threshold):
                break
            m1 -= 1
        return m0,n0,m1,n1

class  MediolateralObliqueSegmenter(Segmenter):
    def __init__(self):
        pass
    def segment(self,pixels,laterality='L'):
        pass

if __name__=='__main__':
    Segmenter.Register('CC', CranioCaudalSegmenter())
    parser = ArgumentParser(__doc__)
    parser.add_argument('image_ids', nargs='+', type=int)
    parser.add_argument('--show', default=False, action='store_true')
    parser.add_argument('--step', default=False, action='store_true')
    args  = parser.parse_args()

    loader   = Loader()
    for image_id in args.image_ids:
        pixels,laterality,view = loader.get_image(image_id=image_id)
        segmenter              = Segmenter.Create(view)
        if segmenter==None: continue
        pixels      = segmenter.standardize_orientation(pixels,laterality=laterality)
        m0,n0,m1,n1 = segmenter.get_bounds(pixels)

        fig      = figure(figsize=(12,8))
        ax1      = fig.add_subplot(1,2,1)
        fig.suptitle(f'{image_id} {laterality} {view}')
        ax1.imshow(pixels, cmap = 'gray')
        ax1.axvline(n1,
                    c         = 'xkcd:blue',
                    linestyle = 'dotted')
        ax1.axhline(m0,
                    c         = 'xkcd:blue',
                    linestyle = 'dotted')
        ax1.axhline(m1,
                    c         = 'xkcd:blue',
                    linestyle = 'dotted')
        ax2 = fig.add_subplot(1,2,2)
        ax2.imshow(pixels[m0:m1,n0:n1], cmap = 'gray')
        if args.step:
            show()
        else:
            if not args.show:
                close(fig)

        if args.show and not args.step:
            show()
