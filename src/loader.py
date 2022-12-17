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

'''Read image from restructured data on drive D'''

from dicomsdl          import open
from matplotlib.pyplot import figure, show
from os                import walk
from os.path           import exists, join
from pandas            import read_csv


class Loader:
    '''
    This class loads images and metadata
    '''
    def __init__(self,
                 path    = r'D:\data\rsna-breast-cancer-detection',
                 dataset = 'train'):
        '''
        Configure loader

        Parameters:
            path       To Aal data
            dataset    train or test
        '''
        self.images_path = join(path,f'{dataset}_images')
        self.master      = read_csv(join(path,f'{dataset}.csv'))

    def get_image(self,
                  image_id   = None,
                  patient_id = None):
        '''
        Load specified image.
        Invert if necessary so PhotometricInterpretation is MONOCHROME1 (i.e. background is white)

        Parameters
            image_id      Indicates image
            patient_id    May be omitted
        Returns:
             pixels      The pixels representing  the image
             laterality  L or R
             view        CC or MLO
        '''
        if patient_id==None:
            row        = self.master[self.master['image_id']==image_id]
            patient_id = int(row['patient_id'])

        dataset                   = open(join(self.images_path,str(patient_id),f'{image_id}.dcm'))
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
        view        = row['view'].values[0]
        laterality  = dataset.getDataElement('ImageLaterality').value(),
        laterality2 = row['laterality'].values[0]
        assert laterality == (laterality2,)
        cancer = row['cancer']
        return pixels,laterality2,view,int(cancer)

def get_all_images(path = r'D:\data\rsna-breast-cancer-detection',
                   dataset = 'train_images'):
    '''A generator for iterating through all images'''
    for dirpath, dirnames, filenames in walk(join(path,dataset)):
        for filename in filenames:
            parts = filename.split('.')
            yield int(parts[0])

if __name__=='__main__':
    loader   = Loader()
    pixels,laterality,view,cancer = loader.get_image(image_id=388811999)
    fig      = figure(figsize=(12,8))
    ax1      = fig.add_subplot(1,1,1)
    ax1.imshow(pixels, cmap = 'gray')
    fig.suptitle(f'{laterality} {view} {cancer}')
    show()
