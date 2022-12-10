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
    Download training dataets with cancers
'''

from argparse          import ArgumentParser
from matplotlib.pyplot import figure, show
from os.path           import exists, join
from pandas            import read_csv
from visualize         import get_bounds

DATA                = '../data'
TRAIN               = join(DATA,'train.csv')
FIGS                = '../docs/figs'


parser = ArgumentParser('Visualize Data',__doc__)
parser.add_argument('--show', default=False, action='store_true')
args = parser.parse_args()

with open('download_cancers.bat','w') as out:
    for _,row in read_csv(TRAIN).iterrows():
        site_id                 = row['site_id']
        patient_id              = row['patient_id']
        image_id                = row['image_id']
        laterality              = row['laterality']
        view                    = row['view']
        age                     = row['age']
        cancer                  = row['cancer']
        biopsy                  = row['biopsy']
        invasive                = row['invasive']
        BIRADS                  = row['BIRADS']
        implant                 = row['implant']
        density                 = row['density']
        machine_id              = row['machine_id']
        difficult_negative_case = row['difficult_negative_case']
        path                    = '../data'
        if cancer==1:
            dcm_file  = join(DATA,f'{image_id}.dcm')
        out.write(f'kaggle competitions download -f train_images/{patient_id}/{image_id}.dcm  -p {path} rsna-breast-cancer-detection\n')


