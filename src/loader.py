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
from numpy             import uint8
from os.path           import exists, join
from pandas            import read_csv

class Window:
    '''
    Apply windowing as specified in dicom file

    snarfed from https://www.kaggle.com/code/omission/eda-view-dicom-images-with-correct-windowing/notebook
    '''
    @staticmethod
    def get_first_element(x):
        if type(x)==list:
            print (x)
            return x[0]
        else:
            return x

    def __init__(self,ds):
        self.RescaleIntercept = ds.getDataElement('RescaleIntercept').value()
        self.RescaleSlope     = ds.getDataElement('RescaleSlope').value()
        self.WindowCenter     = Window.get_first_element(ds.getDataElement('WindowCenter').value())
        self.WindowWidth      = Window.get_first_element(ds.getDataElement('WindowWidth').value())
        self.VOILUTFunction   = ds['VOILUTFunction']
        self.img_min          = self.WindowCenter - self.WindowWidth//2
        self.img_max          = self.WindowCenter + self.WindowWidth//2

    def scale(self,img):
        img_scaled                          = img*self.RescaleSlope +self.RescaleIntercept
        img_scaled[img_scaled<self.img_min] = self.img_min
        img_scaled[img_scaled>self.img_max] = self.img_max
        return img_scaled

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
            path       To all data, train or test
            dataset    train or test
        '''
        self.images_path = join(path,f'{dataset}_images')
        self.master      = read_csv(join(path,f'{dataset}.csv'))

    def get_image_file_name(self,patient_id,image_id):
        return join(self.images_path,str(patient_id),f'{image_id}.dcm')

    def get_image(self,
                  image_id               = None,
                  patient_id             = None,
                  should_apply_windowing = True,
                  show_pixel_data_info   = False):
        '''
        Load specified image.
        Invert if necessary so PhotometricInterpretation is MONOCHROME1 (i.e. background is white)

        Parameters
            image_id                 Indicates image
            patient_id               May be omitted
            should_apply_windowing   Controls whether image should be windows
            show_pixel_data_info     For exploration

        Returns:
             img         The pixels representing  the image
             laterality  L or R
             view        CC or MLO
        '''
        if patient_id==None:
            row        = self.master[self.master['image_id']==image_id]
            patient_id = int(row['patient_id'])

        ds                   = open(self.get_image_file_name(patient_id,image_id))

        if show_pixel_data_info:
            for key in ds:
                print (key,key.repr())
            dump = ds.dump()
            print (dump)
            for key,value in ds.getPixelDataInfo().items():
                print (key,value)
        img                       = ds.pixelData()

        PhotometricInterpretation = ds.getDataElement('PhotometricInterpretation').value()
        SamplesPerPixel           = ds.getDataElement('SamplesPerPixel').value()
        ImageLaterality           = ds.getDataElement('ImageLaterality').value()
        bits_stored = ds["BitsStored"]
        voi_lut_function = ds["VOILUTFunction"]
        window = Window(ds)
        m,n                       = img.shape
        assert m==ds.getDataElement('Rows').value() and n==ds.getDataElement('Columns').value()

        if should_apply_windowing:
            img = window.scale(img)

        view        = row['view'].values[0]
        laterality  = ds.getDataElement('ImageLaterality').value(),
        laterality2 = row['laterality'].values[0]
        assert laterality == (laterality2,)
        cancer = row['cancer']
        img = self.force_monochrome1(PhotometricInterpretation,img)
        return self.normalize(img) if should_apply_windowing else img,laterality2,view,int(cancer)



    def apply_windowing(self,ds,img):
        '''
        Apply windowing as specified in disom file

        snarfed from https://www.kaggle.com/code/omission/eda-view-dicom-images-with-correct-windowing/notebook
        '''
        def get_first_element(x):
            if type(x)==list:
                print (x)
                return x[0]
            else:
                return x

        RescaleIntercept = ds.getDataElement('RescaleIntercept').value()
        RescaleSlope     = ds.getDataElement('RescaleSlope').value()
        img              = img*RescaleSlope +RescaleIntercept
        WindowCenter     = get_first_element(ds.getDataElement('WindowCenter').value())
        WindowWidth      = get_first_element(ds.getDataElement('WindowWidth').value())
        img_min          = WindowCenter - WindowWidth//2
        img_max          = WindowCenter + WindowWidth//2
        img[img<img_min] = img_min
        img[img>img_max] = img_max
        return img

    def force_monochrome1(self,photometricInterpretation,img):
        '''
        Ensure image is PhotometricInterpretation is MONOCHROME1 by forcing MONOCHROME2 to MONOCHROME1
        '''
        assert photometricInterpretation=='MONOCHROME2' or photometricInterpretation=='MONOCHROME1'
        if photometricInterpretation=='MONOCHROME2':
            return img.max() - img
        else:
            return img

    def normalize(self,img):
        '''
        Force image pixels into 0-255
        '''
        if img.max() != 0:
            img = img /img.max()

        return (img * 255).astype(uint8)

def get_all_images(path = r'D:\data\rsna-breast-cancer-detection',
                   dataset = 'train_images'):
    '''A generator for iterating through all images'''
    for dirpath, dirnames, filenames in walk(join(path,dataset)):
        for filename in filenames:
            parts = filename.split('.')
            yield int(parts[0])

if __name__=='__main__':
    loader   = Loader()
    img,laterality,view,cancer = loader.get_image(image_id=797737008)
    img0,_,_,_ = loader.get_image(image_id=797737008,should_apply_windowing=False,show_pixel_data_info=True)
    fig      = figure(figsize=(12,8))
    ax1      = fig.add_subplot(2,2,1)
    ax1.imshow(img0, cmap = 'gray')
    ax2      = fig.add_subplot(2,2,2)
    ax2.hist(img0)

    ax3      = fig.add_subplot(2,2,3)
    ax3.imshow(img, cmap = 'gray')
    fig.suptitle(f'{laterality} {view} {cancer}')
    show()
