# rsna-breast-cancer-detection
[Find breast cancers in screening mammograms](https://www.kaggle.com/competitions/rsna-breast-cancer-detection/leaderboard)

## Current

Folder|File|Description
------|---------------------------------|--------------------------------
docs|rsna&#8209;breast&#8209;cancer&#8209;detection.bib|Bibliography
&nbsp;|rsna&#8209;breast&#8209;cancer&#8209;detection.tex|Notes on project
src|covariance.py|Calculate covariance matrix for possibly interconnected fields: age, cancer, biopsy, invasive, BIRADS, density, and difficult_negative_case.
&nbsp;|segment.py|Segmentation using Dirichlet clustering
&nbsp;|loader.py|Read image from restructured data on drive D
&nbsp;|restructure.py| Restructure downloaded training data so all patient directories exist and are in images in patient files.   Does not download new data.
&nbsp;|segment.py|Separate breast from the rest
&nbsp;|visualize.py|Visualize data
&nbsp;|visualize_train.py|Visualize training data
&nbsp;|visualize_cancers.py|Visualize images with cancer spots
&nbsp;|visualize_pairs.py|Visualize all images for patients with at least one cancer spot
&nbsp;|rsna&#8209;breast&#8209;cancer&#8209;detection.wpr|WingIDE project file

## Old files

Folder|File|Description
------|---------------------------------|--------------------------------
src|download.py|Download selected data from kaggle
&nbsp;|download_cancers.py|Download training datasets with cancers
&nbsp;|expand.py|Extract files from zip archive downloaded from kaggle
&nbsp;|split_batch.py|Utility to split download batch file to work around Kaggle limitations
