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

'''
    Demonstrate reduction of size of pixel array by trimming irrelevant pixels
'''

from argparse          import ArgumentParser
from cv2               import Canny
from dicomsdl          import open
from matplotlib.pyplot import figure, show
from numpy             import all, arange, histogram, iinfo, log, uint8, where, zeros

def get_bounds(pixel_array):
    '''
        Reduce size of pixel array by trimming irrelevant pixels

        Returns:
           Bounding box: xmin,ymin,xmax,ymax

    '''
    def is_background(strip):
        '''Determine whther strip is part of background'''
        if background_low:
            return all(strip<=background)
        else:
            return all(strip>=background)

    hist,bins    = histogram(pixel_array, density=True)

    if hist[0]>hist[-1]:
        background = bins[1]
        background_low = True
    else:
        background = bins[-2]
        background_low = False

    xmin,ymin = 0,0
    xmax,ymax = pixel_array.shape


    while is_background(pixel_array[xmin,:]):
        xmin+= 1
    while is_background(pixel_array[:,ymin]):
        ymin+= 1
    while is_background(pixel_array[xmax-1,:]):
        xmax-=1
    while is_background(pixel_array[:,ymax-1]):
        ymax-= 1

    return xmin,ymin,xmax,ymax, background, background_low



if __name__=='__main__':
    epsilon = 0.000001
    parser = ArgumentParser(__doc__)
    parser.add_argument('--files', nargs='+')
    parser.add_argument('--show', default=False, action='store_true')
    args        = parser.parse_args()
    for file in args.files:
        dataset                        = open(f'../data/{file}.dcm')
        pixels                         = dataset.pixelData()
        xmin,ymin,xmax,ymax,background,background_low = get_bounds(pixels)
        m1                  = pixels[xmin:xmax,ymin:ymax].min()
        m2                  = pixels[xmin:xmax,ymin:ymax].max()
        print (background_low, background, m1, m2)
        scaled              = (pixels[xmin:xmax,ymin:ymax]-m1)/(m2-m1)
        if background_low:
            scaled = 1-scaled
        p8                  = uint8(log(scaled+epsilon))
        edges               = Canny(p8,32,100)

        fig  = figure(figsize=(8,8))
        ax1  = fig.add_subplot(2,2,1)
        ax1.imshow(pixels, cmap = 'gray')
        ax2  = fig.add_subplot(2,2,2)
        ax2.imshow(pixels[xmin:xmax,ymin:ymax], cmap = 'gray')
        ax3  = fig.add_subplot(2,2,3)
        ax3.imshow(edges, cmap = 'gray')
        show()

    if args.show:
        show()
