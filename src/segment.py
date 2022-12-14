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

from argparse          import ArgumentParser
from loader            import Loader
from matplotlib.pyplot import figure, show
from numpy             import flip

class Segmenter:
    @classmethod
    def Create(cls,view):
        if view=='CC':
            return Segmenter()
    def __init__(self):
        pass
    def segment(self,pixels,laterality='L'):
        pixels = self.standardize_orientation(pixels,axis=1)
    def standardize_orientation(self,pixels,laterality='L'):
        if laterality=='R':
            pixels = flip(pixels,axis=1)
        return pixels

if __name__=='__main__':
    parser = ArgumentParser(__doc__)
    parser.add_argument('image_ids', nargs='+', type=int)
    parser.add_argument('--show', default=False, action='store_true')
    args  = parser.parse_args()

    loader   = Loader()
    for image_id in args.image_ids:
        pixels,laterality,view = loader.get_image(image_id=image_id)
        segmenter              = Segmenter.Create(view)
        if segmenter==None: continue
        pixels = segmenter.standardize_orientation(pixels,laterality=laterality)

        fig      = figure(figsize=(12,8))
        ax1      = fig.add_subplot(1,1,1)
        fig.suptitle(f'{image_id} {laterality} {view}')
        ax1.imshow(pixels, cmap = 'gray')
    show()
