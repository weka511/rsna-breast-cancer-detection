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
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

'''
    Visualize training data for cancers
'''

from argparse          import ArgumentParser
from dicomsdl          import open
from loader            import Loader
from matplotlib.pyplot import figure, show
from math              import isqrt
from os.path           import exists, join
from pandas            import read_csv
from visualize         import get_bounds

DATA                = 'D:/data/rsna-breast-cancer-detection'
TRAIN               = join(DATA,'train.csv')
FIGS                = '../docs/figs'


parser = ArgumentParser('Visualize Data',__doc__)
parser.add_argument('--show', default=False, action='store_true')
args = parser.parse_args()

loader = Loader()
df     = read_csv(TRAIN)
processed = set()

for _,row in df.iterrows():
    site_id                 = row['site_id']
    patient_id              = row['patient_id']
    if patient_id in processed: continue
    processed.add(patient_id)
    df_patient            = df[df['patient_id']==patient_id]
    if df_patient['cancer'].any():
        m = isqrt(len(df_patient))
        n = m
        while m*n<len(df_patient):
            n += 1
        k = 0
        for image_id in df_patient['image_id']:
            dcm_file  = loader.get_image_file_name(patient_id,image_id)
            if exists(dcm_file):
                if k==0:
                    fig = figure(figsize=(10,10))
                    fig.suptitle(f'Patient={patient_id}')
                k+= 1
                print (row['site_id'],row['patient_id'],row['image_id'],row['laterality'],dcm_file)
                try:
                    img,laterality,view,cancer = loader.get_image(image_id=image_id)
                    ax = fig.add_subplot(m,n,k)
                    ax.imshow(img, cmap = 'gray')
                    ax.set_title(f'{image_id} {laterality} {view} {cancer}')
                except RuntimeError as e:
                    print (e)
        if k>0:
            fig.savefig(join(FIGS,f'{patient_id}'))

if args.show:
    show()

