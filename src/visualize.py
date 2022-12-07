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

from numpy             import where
from pydicom           import dcmread  # Using 2.4.0dev0
from matplotlib.pyplot import figure, show


dataset     = dcmread('../data/51088550.dcm')
M,N         = dataset.pixel_array.shape
one_d       = dataset.pixel_array.view()
one_d.shape = M*N # Lots of 3044

fig  = figure(figsize=(8,8))
ax1  = fig.add_subplot(2,2,1)
ax1.imshow(dataset.pixel_array)
ax2       = fig.add_subplot(2,2,2)
n,bins,_  = ax2.hist(dataset.pixel_array[:,0],bins=25)
threshold = 0.5*(bins[-2]+bins[-1])
i1,j1 = where(dataset.pixel_array<threshold)
print (i1)
print (max(j1))
# i0,       = where(dataset.pixel_array[:,0]<threshold)
# print (i0[0],i0[-1])
pixel_array_reduced = dataset.pixel_array[i1[0]:i1[-1],:max(j1)]
ax3  = fig.add_subplot(2,2,3)
ax3.imshow(pixel_array_reduced)

show()
