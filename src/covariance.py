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

from matplotlib.pyplot     import figure, show
from os.path               import exists, join
from numpy                 import cov
from pandas                import read_csv
from seaborn               import heatmap, set
from sklearn.preprocessing import StandardScaler


DATA                = '../data'
TRAIN               = join(DATA,'train.csv')
FIGS                = '../docs/figs'

DENSITIES = {'A':0, 'B':1, 'C':2, 'D': 3}



df = read_csv(TRAIN)
df = df.dropna()
df['density'] = df['density'].apply(lambda x:DENSITIES[x])
df['difficult_negative_case'] = df['difficult_negative_case'].apply(lambda x:1 if x else 0)
COLS = ['age', 'cancer', 'biopsy', 'invasive', 'BIRADS', 'implant', 'density', 'difficult_negative_case']

stdsc   = StandardScaler()
X_std   = stdsc.fit_transform(df[COLS].iloc[:,range(0,len(COLS))].values)
cov_mat = cov(X_std.T)

fig = figure(figsize=(8,8))
ax  = fig.add_subplot(1,1,1)
set(font_scale=1.5)
heatmap(cov_mat,
        ax          = ax,
        cbar        = True,
        annot       = True,
        square      = True,
        fmt         = '.2f',
        annot_kws   = {'size': 12},
        yticklabels = COLS,
        xticklabels = COLS)
ax.set_title('Covariance matrix')
# fig.tight_layout()
fig.savefig(join(FIGS,'covariance'))
show()
