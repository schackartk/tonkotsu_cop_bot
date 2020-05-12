"""
Author : schackartk
Purpose: A Bayes Model for Tonkatsu occurence classification
Date   : 23 April 2020
"""

import argparse
import matplotlib.pyplot as plt # Generating graphical confusion matrix
import nltk
import pandas as pd
import os
import pickle
import re # Regular expressions
import seaborn as sn # Generating heatmap

from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB, BernoulliNB

#nltk.download('stopwords')

# --------------------------------------------------
def get_args():
    """Get command-line arguments"""
    parser = argparse.ArgumentParser(
        description='Generate bayesian model for tonkatsu',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        '-d',
        '--data',
        help='Labeled data file',
        metavar='FILE',
        type=str,
        default='data/all_labeled_data.txt')
    
    parser.add_argument(
        '-o',
        '--out',
        help='Name of model output (pickle)',
        metavar='FILE',
        type=str,
        default='MNB_model.pkl')
    
    return parser.parse_args()

# --------------------------------------------------
def clean_title(raw_title):
    """Take title strings and clean them"""
    letters_only = re.sub('[^a-zA-Z]', ' ', raw_title)
    words = letters_only.lower().split()
    stop = set(stopwords.words('english'))
    stop.add('tonkatsu')
    meaningful_words = [w for w in words if w not in stop]
   
    return(" ".join(meaningful_words))

# --------------------------------------------------
def get_features(stng, vec_obj):
    """Get word feature vectors"""
    if vec_obj:
        # Here the vectorizer has already been trained and passed as an arg
        # Need to feed vec_obj into vectorizer function
        # This will be used in the case of testing and in real application
        vectorizer = vec_obj
        features = vectorizer.transform(stng)
    else:
        # Initiate a new CountVectorizer and use it to generate features
        vectorizer = CountVectorizer(analyzer='word',
                                     preprocessor=None,
                                     stop_words='english')
        
        features = vectorizer.fit_transform(stng)
    
    return features, vectorizer

# --------------------------------------------------
def MNB_model_generate(X_train, X_test, y_train): # Multinomial Naive Bayes' Model
    """Train Naive Bayes model"""  
    naive_model = MultinomialNB()
    classifier = naive_model.fit(X_train, y_train)
    
    return classifier
 
# -------------------------------------------------- 
def main():
    """The good stuff"""
    
    # Retrieve command-line arguments from argparse
    args = get_args()
    data_file = args.data
    pkl_file = args.out
    
    raw_data = pd.read_csv(data_file, delimiter='\t', header=0)
    
    titles = []
    for i in range(raw_data.title.size):
        titles.append(clean_title(raw_data.title[i]))

    y = raw_data.label
    
    titles_train, titles_test, y_train, y_test = train_test_split(titles, y,
                                                                  test_size=0.2)
    
    print('Extracting features')
    x_train, vectorizer = get_features(titles_train, None)
    x_test, _ = get_features(titles_test, vectorizer)
    
    print('Training model')
    MNB_model = MNB_model_generate(x_train, x_test, y_train)
    
    print('Testing model')
    MNB_prediction = MNB_model.predict(x_test)
    
    MNB_confusion = confusion_matrix(MNB_prediction, y_test)
    MNB_accuracy = MNB_model.score(x_test, y_test)
    accuracy_per = round(MNB_accuracy*1000)/10
    
    plt.figure(figsize = (10,7))
    sn.heatmap(MNB_confusion, annot=True)
    plt.xlabel('Actual Class')
    plt.ylabel('Predicted Class')
    plt.title('Confusion Matrix \nAccuracy: {}%'.format(accuracy_per), size=14)
    plt.show()
    
    print('Saving test data.')
    if os.path.isfile('test_data.txt'):
        os.remove('test_data.txt')
        
    with open('test_data.txt','a') as fh:
            i = 0
            fh.write('Actual\tPredicted\tTitle\n')
            for ind, label in y_test.items():
                pred = MNB_prediction[i]
                tit = raw_data.title[ind]
                fh.write('{}\t{}\t{}\n'.format(label, pred, tit))
                i += 1
       
    MNB_tuple = (MNB_model, x_test, y_test, MNB_accuracy, vectorizer)
    
    print('Saving pickle')
    with open(pkl_file, 'wb') as file:
        pickle.dump(MNB_tuple, file)
    
    print('Opening pickle')
    with open(pkl_file, 'rb') as file:
        pickle_model, x_test, y_test, pickle_accuracy, vec = pickle.load(file)
        
    score = pickle_model.score(x_test, y_test)
    print('Test score: {}%'.format(100*score))
    print('Saved score: {}%'.format(100*pickle_accuracy))
    


    
# --------------------------------------------------
if __name__ == '__main__':
    main()    