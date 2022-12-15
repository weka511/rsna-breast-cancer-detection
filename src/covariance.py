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

'''
    Calculate covariance matrix for possibly interconnected fields:
    age, cancer, biopsy, invasive, BIRADS, density, and difficult_negative_case.
'''

from matplotlib.pyplot     import figure, show
from os.path               import exists, join
from numpy                 import cov
from pandas                import read_csv
from scipy.stats           import linregress
from seaborn               import heatmap, set
from sklearn.preprocessing import StandardScaler


DATA      = r'd:\data\rsna-breast-cancer-detection'
TRAIN     = join(DATA,'train.csv')
FIGS      = '../docs/figs'
DENSITIES = {'A':0, 'B':1, 'C':2, 'D': 3}
COLS      = ['age',
             'cancer',
             'biopsy',
             'invasive',
             'BIRADS',
             'implant',
             'density',
             'difficult_negative_case'
             ]


df                            = read_csv(TRAIN).dropna()
df['density']                 = df['density'].apply(lambda x:DENSITIES[x])
df['difficult_negative_case'] = df['difficult_negative_case'].apply(lambda x:1 if x else 0)
mean                          = df['cancer'].mean()

result = linregress(df['age'],df['cancer'])
print(f'P(Cancer)={mean}, slope={result.slope}, intercept={result.intercept}, r value={result.rvalue}')

stdsc   = StandardScaler()
X_std   = stdsc.fit_transform(df[COLS].iloc[:,range(0,len(COLS))].values)
cov_mat = cov(X_std.T)

fig     = figure(figsize=(8,8))
ax      = fig.add_subplot(1,1,1)
set(font_scale=1.5)
labels  = COLS[:-1] + ['difficult']
heatmap(cov_mat,
        vmin        = -1,
        vmax        = +1,
        cmap        = 'seismic',
        ax          = ax,
        cbar        = False,
        annot       = True,
        square      = True,
        fmt         = '.2f',
        annot_kws   = {'size': 12},
        yticklabels = labels,
        xticklabels = labels)

fig.tight_layout()
fig.savefig(join(FIGS,'covariance'))
show()
