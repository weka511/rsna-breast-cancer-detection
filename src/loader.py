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

'''Read image from restructured data on drive D'''

from abc               import ABC,abstractmethod
from dicomsdl          import open
from matplotlib.pyplot import figure, show
from numpy             import exp, uint8
from os                import walk
from os.path           import exists, join
from pandas            import read_csv
from warnings          import warn

class VOILUT(ABC):
    '''
    A class to implement the VOI LUT functiionality described in the DICOM standard
    https://dicom.nema.org/medical/dicom/2018b/output/chtml/part03/sect_C.11.2.html#equation_C.11-1
    '''
    @staticmethod
    def get_first_element(x):
        if type(x)==list:
            return x[0]
        else:
            return x

    @classmethod
    def create(cls,ds):
        VOILUTFunction   = ds['VOILUTFunction']
        if VOILUTFunction=='SIGMOID':
            return Sigmoid(ds)
        elif VOILUTFunction=='LINEAR_EXACT':
            return LinearExact(ds)
        else:
            return Linear(ds)

    def __init__(self,ds):
        self.WindowCenter     = VOILUT.get_first_element(ds.getDataElement('WindowCenter').value())
        self.WindowWidth      = VOILUT.get_first_element(ds.getDataElement('WindowWidth').value())

    @abstractmethod
    def scale(self,img):
        ...


class Linear(VOILUT):
    '''
    If VOI LUT Function (0028,1056) is absent or has a value of LINEAR, Window Center (0028,1050) and Window Width (0028,1051)
    specify a linear conversion from stored pixel values (after any Modality LUT or Rescale Slope and Intercept specified
    in the IOD have been applied) to values to be displayed. Window Center contains the input value that is the center
    of the window. Window Width contains the width of the window.

    if (x <= c - 0.5 - (w-1) /2), then y = ymin

    else if (x > c - 0.5 + (w-1) /2), then y = ymax

    else y = ((x - (c - 0.5)) / (w-1) + 0.5) * (ymax- ymin) + ymin

    '''
    def __init__(self,ds):
        super().__init__(ds)
        self.RescaleIntercept = ds.getDataElement('RescaleIntercept').value()
        self.RescaleSlope     = ds.getDataElement('RescaleSlope').value()

    def scale(self,img):
        img_min                        = self.WindowCenter - self.WindowWidth//2
        img_max                        = self.WindowCenter + self.WindowWidth//2
        img_scaled                     = img*self.RescaleSlope +self.RescaleIntercept
        img_scaled[img_scaled<img_min] = img_min
        img_scaled[img_scaled>img_max] = img_max
        return img_scaled

class Sigmoid(VOILUT):
    '''
    If the value of VOI LUT Function (0028,1056) is SIGMOID, the function to be used to convert the output of the
    (conceptual) Modality LUT values to the input of the (conceptual) Presentation LUT is given by Equation C.11-1.
    '''
    def __init__(self,ds):
        super().__init__(ds)
        BitsStored       = ds.getDataElement('BitsStored').value()
        self.OutputRange = 2**BitsStored-1

    def scale(self,img):
        scaled1 = (img-self.WindowCenter)/self.WindowWidth
        return self.OutputRange/(1+exp(-4*scaled1))

class LinearExact(Linear):
    '''
    If the value of VOI LUT Function (0028,1056) is LINEAR_EXACT, the function to be used to convert the output
    of the (conceptual) Modality LUT values to the input of the (conceptual) Presentation LUT is given by the
    following pseudo-code, where x is the input value, y is an output value with a range from ymin to ymax,
    c is Window Center (0028,1050) and w is Window Width (0028,1051):

    if (x <= c - w/2), then y = ymin

    else if (x > c + w/2), then y = ymax

    else y = (x - c) / w * (ymax- ymin) + ymin

    AFAIK, this VOI LUT function is not actually used.

    '''
    def __init__(self,ds):
        super().__init__(ds)
        warn('LINEAR_EXACT not implemented: using LINEAR_instead.')

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

        ds  = open(self.get_image_file_name(patient_id,image_id))

        if show_pixel_data_info:
            dump = ds.dump()
            print (dump)
            for key,value in ds.getPixelDataInfo().items():
                print (key,value)

        img                       = ds.pixelData()

        PhotometricInterpretation = ds.getDataElement('PhotometricInterpretation').value()
        SamplesPerPixel           = ds.getDataElement('SamplesPerPixel').value()
        window                    = VOILUT.create(ds)
        m,n                       = img.shape
        assert m==ds.getDataElement('Rows').value() and n==ds.getDataElement('Columns').value()

        view        = row['view'].values[0]
        ImageLaterality  = ds.getDataElement('ImageLaterality').value(),
        RowLaterality = row['laterality'].values[0]
        assert ImageLaterality == (RowLaterality,)
        cancer = row['cancer']
        img = self.force_monochrome1(PhotometricInterpretation,img)
        return self.normalize(window.scale(img)) if should_apply_windowing else img,RowLaterality,view,int(cancer)


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
    img0,_,_,_ = loader.get_image(image_id               = 797737008,
                                  should_apply_windowing = False,
                                  show_pixel_data_info   = True)
    fig      = figure(figsize=(12,8))
    ax1      = fig.add_subplot(2,2,1)
    ax1.imshow(img0, cmap = 'gray')
    ax2      = fig.add_subplot(2,2,2)
    ax2.hist(img0)

    ax3      = fig.add_subplot(2,2,3)
    ax3.imshow(img, cmap = 'gray')
    fig.suptitle(f'{laterality} {view} {cancer}')
    show()
