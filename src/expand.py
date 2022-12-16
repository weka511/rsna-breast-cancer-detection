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

'''Extract files from zip archive downloaded from kaggle'''

from os      import rename, walk
from os.path import join
from zipfile import ZipFile

PATH = r'D:\data\rsna-breast-cancer-detection/'

z = ZipFile(join(PATH,'part.zip'))
for filename in z.namelist():
    print (filename)
    parts = filename.split('_')
    z.extract(filename,path=join(PATH,'train',parts[0]))

for  dirpath, _, filenames in walk(join(PATH,'train')):
    for filename in filenames:
        parts = filename.split('_')
        if len(parts)>1:
            print (dirpath, filename, parts[1])
            rename(join(dirpath,filename),join(dirpath,parts[1]))
