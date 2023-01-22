#!/usr/bin/env python

# MIT License

# Copyright (c) 2023 Simon Crase

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


from argparse          import ArgumentParser
from cv2               import resize, INTER_CUBIC
from loader            import get_all_images,  Loader
from matplotlib.pyplot import figure, show
from numpy             import argmax, argmin, argsort, array, histogram, zeros
from numpy.linalg      import norm
from numpy.random      import default_rng
from os.path           import join
from os                import walk
from sys               import float_info

class Component:
    def __init__(self,point):
        self.centroid = point
        self.points   = [point]

    def add(self,point):
        self.points.append(point)
        m             = len(self.points)
        self.centroid = ((m-1)* self.centroid + point)/m

    def get_distance(self,component):
        distance = float_info.max
        for pt1 in self.points:
            for pt2 in component.points:
                distance = min(distance,norm(pt1-pt2))
        return distance

class Segmenter:
    def __init__(self,seed=None):
        self.n                    = []
        self.bins                 = []
        self.points               = []
        self.rng                  = default_rng(seed=seed)
        self.components           = []
        self.connected_components = []

    def segment(self,img):
        self.create_foreground(img,get_threshold(img))

    def get_threshold(self,img):
        self.n,self.bins = histogram(img.ravel(),bins=64)
        ithreshold = argmax(self.n)
        return self.bins[ithreshold-1]

    def create_foreground(self,img,threshold):
        m,n = img.shape
        for i in range(m):
            for j in range(n):
                if img[i,j]<threshold:
                    self.points.append((i,j))

    def samples(self,size=1):
        for i in self.rng.integers(low=0, high=len(self.points), size=size):
            yield array(self.points[i])

    def create_components(self,N=1024,lambda_=32):
        for sample in self.samples(size=N):
            if len(self.components)==0:
                self.components.append(Component(sample))
            else:
                nearest_component,distance = self.get_nearest_component(sample)
                if distance<lambda_:
                    nearest_component.add(sample)
                else:
                    self.components.append(Component(sample))

    def get_nearest_component(self,sample):
        distances = [norm(component.centroid-sample) for component in self.components]
        index     = argmin(distances)
        return self.components[index],distances[index]

    def connect_components(self,distances,min_gap=2):
        to_connect      = set(range(len(self.components)))
        connected       = {}
        open_components = []
        while len(to_connect)>0:
            i = to_connect.pop()
            connected[i] = [i]
            for j in to_connect:
                if distances[i,j] < min_gap:
                    open_components.append(j)
            for j in open_components:
                if j in to_connect:
                    to_connect.remove(j)
            while len(open_components)>0:
                successors = []
                for j in open_components:
                    connected[i].append(j)
                    connected[j] = connected[i]
                    to_remove=[]
                    for k in to_connect:
                        if distances[j,k] < min_gap:
                            successors.append(k)
                            to_remove.append(k)
                    for k in to_remove:
                        to_connect.remove(k)
                open_components = successors

        connected_components0 = []
        duplicates            = set()
        for key,values in connected.items():
            if not key in duplicates:
                connected_components0.append(values)
                for value in values:
                    duplicates.add(value)
        sizes = [len(c) for c in connected_components0]
        self.connected_components = [connected_components0[i] for i in argsort(sizes)[::-1]]

    def create_distances(self):
        n       = len(self.components)
        product = zeros((n,n))
        for i in range(n):
            for j in range(i,n):
                product[i,j] = self.components[i].get_distance(self.components[j])
                product[j,i] = product[i,j]
        return product

if __name__=='__main__':
    FIGS   = '../docs/figs'
    parser = ArgumentParser(__doc__)
    parser.add_argument('image_ids', nargs='*', type=int, default=[])
    parser.add_argument('--show', default=False, action='store_true')
    args      = parser.parse_args()
    loader    = Loader()

    for image_id in args.image_ids if len(args.image_ids)>0 else get_all_images():
        print (image_id)
        segmenter = Segmenter()
        img,_,_,_ = loader.get_image(image_id = image_id)
        resized   = resize(img,
                           dsize         = (128, 128),
                           interpolation = INTER_CUBIC)

        threshold = segmenter.get_threshold(resized)
        segmenter.create_foreground(resized,threshold)
        segmenter.create_components()
        segmenter.connect_components(segmenter.create_distances())

        fig = figure(figsize=(8,8))
        fig.suptitle(f'{image_id}')

        ax1 = fig.add_subplot(2,2,1)
        ax1.imshow(resized, cmap = 'gray')

        ax2 = fig.add_subplot(2,2,2)
        ax2.stairs(segmenter.n,segmenter.bins,fill=True)
        ax2.axvline(x     = threshold,
                    c     = 'xkcd:red',
                    label = 'Threshold',
                    ls    = ':')
        ax2.legend()

        ax3 = fig.add_subplot(2,2,3)
        xs = [128-x-1 for x,_ in segmenter.points]
        ys = [y for _,y in segmenter.points]
        ax3.scatter(ys,xs,s=1)
        ax3.set_xlim(ax1.get_xlim())
        y0,y1 = ax1.get_ylim()
        ax3.set_ylim(y1,y0)
        for i,component in  enumerate(segmenter.components):
            xs = [128-x-1 for x,y in component.points]
            ys = [y for x,y in component.points]
            ax3.scatter(ys,xs,label=f'{i+1}')
        ax3.legend()

        ax4 = fig.add_subplot(2,2,4)
        for i,connected in  enumerate(segmenter.connected_components):
            xs = []
            ys = []
            for j in connected:
                component = segmenter.components[j]
                for x,y in component.points:
                    xs.append(128-x-1)
                    ys.append(y)
            ax4.scatter(ys,xs,label=f'{i+1}')
        ax4.legend()

        fig.savefig(join(FIGS,f'dirichlet-{image_id}'))
        if not args.show:
            close(fig)

    if args.show:
        show()
