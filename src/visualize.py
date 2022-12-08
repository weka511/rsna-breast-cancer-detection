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

from numpy             import histogram, where
from pydicom           import dcmread  # Using 2.4.0dev0
from matplotlib.pyplot import figure, show

def trim(pixel_array,
         xpad = 50,
         ypad = 50):
    '''
        Reduce size of pixel array by trimming irrelevant pixels
    '''
    n,bins    = histogram(pixel_array[:,0],bins=25)
    threshold = 0.5*(bins[-2]+bins[-1])
    i1,j1     = where(pixel_array<threshold)
    return pixel_array[i1[0]-xpad:i1[-1]+xpad,:max(j1)+ypad]

if __name__=='__main__':
    dataset     = dcmread('../data/51088550.dcm')
    M,N         = dataset.pixel_array.shape
    one_d       = dataset.pixel_array.view()
    one_d.shape = M*N # Lots of 3044

    fig  = figure(figsize=(8,8))
    ax1  = fig.add_subplot(2,2,1)
    ax1.imshow(dataset.pixel_array)
    ax2  = fig.add_subplot(2,2,2)
    ax2.hist(dataset.pixel_array[:,0],bins=25)
    ax3  = fig.add_subplot(2,2,3)
    trimmed = trim(dataset.pixel_array)
    ax3.imshow(trimmed)
    m,n = trimmed.shape
    m1,n1 = dataset.pixel_array.shape
    ax3.set_title(fr'{m}$\times${n}: {m1}$\times${n1}$\rightarrow${100*m*n/(m1*n1):.0f}%')

    show()
