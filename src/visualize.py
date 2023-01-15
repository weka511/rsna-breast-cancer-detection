#!/usr/bin/env python

# MIT License

# Copyright (c) 2022-2023 Simon Crase

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
from dicomsdl          import open
from matplotlib.pyplot import figure, show
from numpy             import all, arange, flip, histogram, log,  where, zeros

def get_image(file,path='data'):
    '''
    Read image from specified file, verify keywords are consistent with image, and normalize so background is high
    '''
    dataset                   = open(f'../{path}/{file}.dcm')
    pixels                    = dataset.pixelData()
    PhotometricInterpretation = dataset.getDataElement('PhotometricInterpretation').value()
    SamplesPerPixel           = dataset.getDataElement('SamplesPerPixel').value()
    ImageLaterality           = dataset.getDataElement('ImageLaterality').value()
    Rows                      = dataset.getDataElement('Rows').value()
    Columns                   = dataset.getDataElement('Columns').value()
    m,n                       = pixels.shape
    assert m==dataset.getDataElement('Rows').value() and n==dataset.getDataElement('Columns').value()
    if dataset.getDataElement('PhotometricInterpretation').value()=='MONOCHROME2':
        pixels = pixels.max() - pixels
    if dataset.getDataElement('ImageLaterality').value()=='R':
        pixels = flip(pixels,axis=1)
    return pixels

def get_bounds(pixel_array):
    '''
        Reduce size of pixel array by trimming irrelevant pixels

        Returns:
           Bounding box: xmin,ymin,xmax,ymax

    '''
    def is_background(strip):
        '''Determine whether strip is part of background'''
        if background_low:
            return all(strip<=background)
        else:
            return all(strip>=background)

    hist,bins    = histogram(pixel_array, density=True)

    if hist[0]>hist[-1]:
        background = bins[0]
        background_low = True
    else:
        background = bins[-1]
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

    return xmin,ymin,xmax,ymax, background

def get_centre_of_mass(pixels,step=16):
    '''
    Calculate weighted average of coordinates within image, weighted by pixel intensity
    '''
    x_total    = 0
    y_total    = 0
    mass_total = 0
    m,n        = pixels.shape
    for i in range(0,m,step):
        for j in range(0,n,step):
            x_total    += i*pixels[i,j]
            y_total    += j*pixels[i,j]
            mass_total += pixels[i,j]
    return x_total/mass_total, y_total/mass_total

def get_path(p0,p1,scaled):
    '''
    Draw a path between to points, and return pixels values along path
    '''
    x0,y0 = p0
    x1,y1 = p1
    m,n   = scaled.shape

    if int(x0)<x1:   # We always process in order of ascending x
        m0 = int(x0)
        n0 = int(y0)
        m1 = int(x1)
        n1 = int(y1)
        must_reverse = False  # This allows us to return values from p0 to p1, irregardless
    else:
        m0 = int(x1)
        n0 = int(y1)
        m1 = int(x0)
        n1 = int(y0)
        must_reverse = True

    # FIXME: this code has too many special cases for my liking
    if abs(m1-m0)>0:
        xs = [i for i in range(m0,m1)]
        ys = [min(n0 + int((i-m0)*(n1-n0)/(m1-m0)),n-1) for i in xs]
    else:
        if n0>n1:
            n0,n1=n1,n0
            m0,m1=m1,m0
        ys = [j for j in range(n0,n1)]
        xs = [min(m0 + int((j-n0)*(m1-m0)/(n1-n0)),m-1) for j in ys]

    if must_reverse:
        xs = xs[::-1]
        ys = ys[::-1]

    return xs,ys,[scaled[i,j] for (i,j) in zip(xs,ys) if i<m and j < n] #FIXME - shouldn't need if


def get_transitions(xs,ys,zs,pixels,background,epsilon=0.001):
    '''
    Fined transitions between background and foreground
    '''
    seeking_background = True
    transitions        = []
    runs               = []
    index              = len(zs) - 1
    run_length         = 0
    while index>0:
        if seeking_background:
            while index>0 and zs[index]>=background-epsilon:
                index-=1
                run_length+=1
        else:
            while index>0 and zs[index]<background-epsilon:
                index-=1
                run_length+=1
        transitions.append(index)
        runs.append(run_length)
        run_length = 0
        if index==0:
            return transitions,runs
        seeking_background = not seeking_background
        index -= 1
    return transitions,runs


if __name__=='__main__':
    XKCD_COLOURS = [
        'xkcd:purple',     'xkcd:green',
        'xkcd:blue',       'xkcd:pink',
        'xkcd:brown',      'xkcd:red',
        'xkcd:light blue',  'xkcd:teal']
    parser = ArgumentParser(__doc__)
    parser.add_argument('--files', nargs='+')
    parser.add_argument('--show', default=False, action='store_true')
    parser.add_argument('--step', default=False, action='store_true')
    args  = parser.parse_args()

    for file in args.files:
        pixels                         = get_image(file)
        xmin,ymin,xmax,ymax,background = get_bounds(pixels)
        m1                             = pixels[xmin:xmax,ymin:ymax].min()
        m2                             = pixels[xmin:xmax,ymin:ymax].max()
        scaled_pixels                  = (pixels[xmin:xmax,ymin:ymax]-m1)/(m2-m1)
        scaled_background              = (background - m1)/(m2-m1)
        x_c, y_c                       = get_centre_of_mass(scaled_pixels)
        m,n                            = scaled_pixels.shape
        ends                           = [[0,0], [int(x_c),0],
                                          [m,0], [m,int(y_c)],
                                          [m,n], [int(x_c),n],
                                          [0,n], [0,int(y_c)]]

        fig  = figure(figsize=(12,8))
        ax1  = fig.add_subplot(3,4,1)
        ax1.imshow(scaled_pixels, cmap = 'gray')

        for k,(x,y) in enumerate(ends):
            ax1.plot([y_c,y],[x_c,x],
                     c         = XKCD_COLOURS[k],
                     marker    = '+',
                     linewidth = 1)

            xs,ys,zs = get_path((x_c,y_c),(x,y),scaled_pixels)
            ax4  = fig.add_subplot(3,4,k+2)
            ax4.plot(zs, c = XKCD_COLOURS[k])
            ax4.hlines(scaled_background,0,len(zs),
                       colors     = 'xkcd:black',
                       linestyles = 'dotted',
                       color      = 'xkcd:black')
            if len(zs)>256:  #FIXME magic number
                transitions,runs = get_transitions(xs,ys,zs,pixels,scaled_background)
                print (k, transitions, runs)
                if len(transitions)==2 and runs[0]>10 and runs[1]>10:  #FIXME magic number
                    x0 = xs[transitions[0]]
                    y0 = ys[transitions[0]]
                    ax1.scatter([y0],[x0],
                                c      = XKCD_COLOURS[k],
                                marker = 'x')


        if args.step:
            show()

    if args.show and not args.step:
        show()
