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
    Restructure downloaded training data so all patient directories exist and images are in in patient files.
    Does not download new data.
'''
from os.path import exists, join
from pandas  import read_csv
from pathlib import Path
from shutil  import move
PATH     = r'D:\data\rsna-breast-cancer-detection'
MASTER   = read_csv(join(PATH,'train.csv'))
SUB_PATH =  join(PATH,'train')

for index,row in MASTER.iterrows():
    patient_id = row['patient_id']
    image_id   = row['image_id']
    patient_path = join(SUB_PATH,str(patient_id))
    if not exists(patient_path):
        Path(join(patient_path)).mkdir(parents=True, exist_ok=True)
    assert exists(patient_path)
    file_path = join(patient_path,f'{image_id}.dcm')
    if not exists(file_path):
        downloaded_path = join(SUB_PATH,f'{image_id}.dcm')
        if exists(downloaded_path):
            print (f'moving {downloaded_path} to {file_path}')
            move(downloaded_path,file_path)
