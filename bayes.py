"""
Author : schackartk
Purpose: A Bayes Model for Tonkatsu occurence classification
Date   : 23 April 2020
"""


import matplotlib.pyplot as plt # Generating graphical confusion matrix
import pandas as pd
import os
import re # Regular expressions
import seaborn as sn # Generating heatmap

from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB, BernoulliNB

#nltk.download('stopwords')

def clean_title(raw_title):
    """Take title strings and clean them"""
    letters_only = re.sub('[^a-zA-Z]', ' ', raw_title)
    words = letters_only.lower().split()
    stop = set(stopwords.words('english'))
    meaningful_words = [w for w in words if w not in stop]
   
    return(" ".join(meaningful_words))

# --------------------------------------------------
def get_features(titles):
    """Get word feature vectors"""  
    vectorizer = CountVectorizer(analyzer='word',
                                 preprocessor=None,
                                 stop_words='english')
    
    features = vectorizer.fit_transform(titles)
    features = features.toarray()
    
    return features

# --------------------------------------------------
def generate_model(X_train, X_test, y_train):
    """Train Naive Bayes model"""  
    naive_model = MultinomialNB()
    classifier = naive_model.fit(X_train, y_train)
    
    
    return classifier
 
# -------------------------------------------------- 
def main():
    """The good stuff"""    
    
    raw_data = pd.read_csv('data/all_labeled_data.txt',
                               delimiter='\t',
                               header=0)
    
    titles = []
    for i in range(raw_data.title.size):
        titles.append(clean_title(raw_data.title[i]))
    
    x = get_features(titles)
    y = raw_data.label
    
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.25)
    
    trained_model = generate_model(x_train, x_test, y_train)
        
    prediction = trained_model.predict(x_test)
    
    cm = confusion_matrix(prediction, y_test)
    plt.figure(figsize = (10,7))
    sn.heatmap(cm, annot=True)
    
    accuracy = cm.trace()/cm.sum()
    print('Accuracy is: {}'.format(accuracy))
    
# --------------------------------------------------
if __name__ == '__main__':
    main()    