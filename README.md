# rsna-breast-cancer-detection
[Find breast cancers in screening mammograms](https://www.kaggle.com/competitions/rsna-breast-cancer-detection/leaderboard)

Folder|File|Description
------|---------------------------------|--------------------------------
docs|rsna&#8209;breast&#8209;cancer&#8209;detection.bib|Bibliography
&nbsp;|rsna&#8209;breast&#8209;cancer&#8209;detection.tex|Notes on project
src|covariance.py|Calculate covariance matrix for possibly interconnected fields: age, cancer, biopsy, invasive, BIRADS, density, and difficult_negative_case.
&nbsp;|download.py|Download selected data from kaggle
&nbsp;|download_cancers.py|Download training dataets with cancers
&nbsp;|restructure.py| Restructure downloaded training data so all patient directories exist and are in images in patient files.   Does not download new data.
&nbsp;|visualize.py|Visualize data
&nbsp;|visualize_train.py|Visualize training data
&nbsp;|visualize_cancers.py|Visualize images with cancer spots
&nbsp;|rsna&#8209;breast&#8209;cancer&#8209;detection.wpr|WingIDE project file
data|sample_submission.csv|Shows format for submission
&nbsp;|test.csv|Test data (without images)
&nbsp;|train.csv|Training data (without images)
