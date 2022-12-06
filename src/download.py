#!/usr/bin/env python

TYPE   = 'train_images'

def download(name,out):
    parts = name.split('/')
    if parts[0].startswith(TYPE):
        out.write(f'kaggle competitions download -f {name} rsna-breast-cancer-detection\n')

with open('download.bat','w') as out,open('../data/files.txt') as f:
    for line in f:
        name = line.split()[0]
        if name.endswith('dcm'):
            download(name,out)

