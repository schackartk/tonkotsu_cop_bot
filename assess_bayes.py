#!/usr/bin/env python3
"""
Author : schackartk
Purpose: Get a better idea of model accuracy by running a lot
Date   : 6 June 2020
"""

import matplotlib.pyplot as plt
import numpy as np
import os
import seaborn as sn 

from sklearn.metrics import confusion_matrix

prg = 'python bayes.py'
n_iter = 100

# for i in range(n_iter):
#     out_f = 'data/test/model{}.pkl'.format(i)
#     test_data = 'data/test/test_data{}.txt'.format(i)

#     os.system('{} -o {} -t {} '.format(prg, out_f, test_data))

actuals = []
preds = []
accuracies = []

for i in range(n_iter):
    with open('data/test/test_data{}.txt'.format(i)) as fh:
        next(fh)
        
        act_vect = []
        pred_vect = []
        
        for line in fh.read().splitlines():
            act, pred, _ = line.split('\t')
            act_vect.append(act)
            pred_vect.append(pred)
          
        conf = confusion_matrix(act_vect, pred_vect, normalize='true')
        acc = (conf[0][0] + conf[1][1]) / 2
        
        preds = preds + pred_vect
        actuals = actuals + act_vect
        accuracies.append(acc)

print(accuracies)
acc_avg = np.average(accuracies)
acc_std = np.std(accuracies)
print(acc_avg)
print(acc_std)
conf = confusion_matrix(actuals,
                        preds,
                        normalize='true')

plt.figure(figsize = (10,7))
sn.heatmap(conf, annot=True, cmap=plt.cm.Blues)
plt.xlabel('Predicted Class')
plt.ylabel('Actual Class')
plt.title('Confusion Matrix \nAccuracy: %', size=14)
plt.show()