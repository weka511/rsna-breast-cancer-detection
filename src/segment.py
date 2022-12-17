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

'''Get rid of irrelevant pixels and focus on tissue'''

from abc               import ABC, abstractmethod
from argparse          import ArgumentParser
from loader            import Loader, get_all_images
from matplotlib.pyplot import close, figure, show
from numpy             import all, any, argmax, argmin, count_nonzero, flip
from os.path           import join
from os                import walk

class Segmenter(ABC):
    '''Get rid of irrelevant pixels and focus on tissue'''

    Segmenters = {}

    @classmethod
    def Register(cls,segmenter):
        '''Store reference to a segmenter so it can be located'''
        Segmenter.Segmenters[segmenter.key] = segmenter

    @classmethod
    def Create(cls,view):
        '''Find appropriate segmenter'''
        if view in Segmenter.Segmenters:
            return Segmenter.Segmenters[view]

    def segment(self,pixels):
        '''Method to get rid of irrelevant pixels and focus on tissue'''
        pixels      = self._standardize_orientation(pixels,axis=1)
        m0,n0,m1,n1 = segmenter._get_bounds(pixels)
        return pixels [m0:m1,n0:n1]

    def _standardize_orientation(self,pixels):
        m,n = pixels.shape
        m0, n0 = self._get_centre_of_mass(pixels)
        if n0>n/2:
            pixels = flip(pixels,axis=1)
        return pixels


    @abstractmethod
    def _get_bounds(self,pixels,epsilon=0.01):
        ...

    def _get_centre_of_mass(self,pixels,step=16):
        '''
        Calculate average of coordinates within image, weighted by pixel intensity
        '''
        x_total    = 0
        y_total    = 0
        mass_total = 0
        m,n        = pixels.shape
        background = pixels.max()
        for i in range(0,m,step):
            for j in range(0,n,step):
                mass        = background - pixels[i,j]
                x_total    += i*mass
                y_total    += j*mass
                mass_total += mass
        return int(x_total/mass_total), int(y_total/mass_total)


class CranioCaudalSegmenter(Segmenter):
    '''Get rid of irrelevant pixels from Cranio Caudal View and focus on tissue'''

    def __init__(self,key ='CC'):
        self.key = key

    def _get_bounds(self,pixels,epsilon=0.01):
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
    '''Get rid of irrelevant pixels from Mediolateral Oblique View and focus on tissue'''

    def __init__(self,key = 'MLO'):
        self.key = key

    def _get_bounds(self,pixels,epsilon=0.01):
        threshold = pixels.max() - epsilon
        m,n       = pixels.shape
        m0,n0     = 0,0
        n1        = n-1
        nfigure   = count_nonzero(pixels<threshold,axis=1)
        n_max     = argmax(nfigure)
        n1 = nfigure[n_max]
        m1        = argmin(nfigure[n_max:-10]) + n_max
        return m0,n0,m1,n1



if __name__=='__main__':
    FIGS      = '../docs/figs'
    Segmenter.Register(CranioCaudalSegmenter())
    Segmenter.Register(MediolateralObliqueSegmenter())
    Segmenter.Register(MediolateralObliqueSegmenter(key='AT'))
    Segmenter.Register(MediolateralObliqueSegmenter(key='LM'))
    Segmenter.Register(MediolateralObliqueSegmenter(key='ML'))
    Segmenter.Register(MediolateralObliqueSegmenter(key='LMO'))
    parser = ArgumentParser(__doc__)
    parser.add_argument('image_ids', nargs='*', type=int)
    parser.add_argument('--views', nargs='*')
    parser.add_argument('--show', default=False, action='store_true')
    parser.add_argument('--step', default=False, action='store_true')
    args   = parser.parse_args()
    loader = Loader()
    image_ids = args.image_ids if len(args.image_ids)>0 else get_all_images()
    for image_id in image_ids:
        pixels,laterality,view,cancer = loader.get_image(image_id=image_id)
        if args.views==None or len(args.views)==0 or view in args.views:
            segmenter              = Segmenter.Create(view)
            fig                    = figure(figsize=(12,8))
            ax1                    = fig.add_subplot(1,2,1)
            fig.suptitle(f'{image_id} {laterality} {view} {cancer}')
            pixels      = segmenter._standardize_orientation(pixels)
            ax1.imshow(pixels, cmap = 'gray')

            m0,n0,m1,n1 = segmenter._get_bounds(pixels)

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
            fig.savefig(join(FIGS,f'segment-{image_id}'))
            if args.step:
                show()
            else:
                if not args.show:
                    close(fig)

        if args.show and not args.step:
            show()
