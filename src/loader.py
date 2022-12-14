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

from dicomsdl          import open
from matplotlib.pyplot import figure, show
from os.path           import exists, join
from pandas            import read_csv


class Loader:
    def __init__(self,
                 path = r'D:\data\rsna-breast-cancer-detection',
                 dataset = 'train'):
        self.images_path   = join(path,dataset)
        self.master = read_csv(join(path,f'{dataset}.csv'))

    def get_image(self,image_id=None,patient_id=None):
        if patient_id==None:
            row = self.master[self.master['image_id']==image_id]
            patient_id = int(row['patient_id'])
        path = join(self.images_path,str(patient_id),f'{image_id}.dcm')
        dataset = open(path)
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
        # if dataset.getDataElement('ImageLaterality').value()=='R':
            # pixels = flip(pixels,axis=1)
        return pixels,dataset.getDataElement('ImageLaterality').value(),row['laterality'].values[0],row['view'].values[0]


if __name__=='__main__':
    loader   = Loader()
    pixels,laterality,laterality2,view = loader.get_image(image_id=388811999)
    fig      = figure(figsize=(12,8))
    ax1      = fig.add_subplot(1,1,1)
    ax1.imshow(pixels, cmap = 'gray')
    fig.suptitle(f'{laterality} {laterality2} {view}')
    show()
