#!/usr/bin/env python3
"""
Author : schackartk
Purpose: A reddit bot for spreading awareness of the misspelling of 'tonkotsu'
Date   : 6 June 2020
"""

import matplotlib.pyplot as plt
import os
import seaborn as sn 

from sklearn.metrics import confusion_matrix

prg = 'python bayes.py'
n_iter = 25

# for i in range(n_iter):
#     out_f = 'data/test/model{}.pkl'.format(i)
#     test_data = 'data/test/test_data{}.txt'.format(i)
    
#     os.system('{} -o {} -t {} '.format(prg, out_f, test_data))

actuals = []
preds = []

for i in range(n_iter):
    with open('data/test/test_data{}.txt'.format(i)) as fh:
        next(fh)
        for line in fh.read().splitlines():
            if line:
                act, pred, _ = line.split('\t')
                preds.append(pred)
                actuals.append(act)

conf = confusion_matrix(actuals,
                        preds,
                        normalize='true')
print(conf)
plt.figure(figsize = (10,7))
sn.heatmap(conf, annot=True, cmap=plt.cm.Blues)
plt.xlabel('Predicted Class')
plt.ylabel('Actual Class')
plt.title('Confusion Matrix \nAccuracy: %', size=14)
plt.show()