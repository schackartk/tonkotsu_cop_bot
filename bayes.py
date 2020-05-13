"""
Author : schackartk
Purpose: A Bayes Model for Tonkatsu occurence classification
Date   : 23 April 2020
"""

import argparse
import matplotlib.pyplot as plt # Generating graphical confusion matrix
import nltk # Natural language toolkit - for getting stopwords
import pandas as pd
import os # Working with files
import pickle # Saving model for reuse
import re # Regular expressions
import seaborn as sn # Generating heatmap

from nltk.corpus import stopwords 
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB

# Downloading stopwords doesn't need to be run every time
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
        default='data/model.pkl')
    
    parser.add_argument(
        '-t',
        '--test_out',
        help='Test data output file',
        metavar='FILE',
        type=str,
        default='data/test_data.txt')
    
    parser.add_argument(
        '-s',
        '--test_split',
        help='Test data split ratio',
        metavar='FLOAT',
        type=str,
        default=0.2)
    
    return parser.parse_args()

# --------------------------------------------------
def warn(msg):
    """Print a message to STDERR"""
    print(msg, file=sys.stderr)

# --------------------------------------------------
def die(msg='Something bad happened'):
    """warn() and exit with error"""
    warn(msg)
    sys.exit(1)

# --------------------------------------------------
def clean_title(raw_title):
    """Take title strings and clean them"""
    # Ignore anything that is not in alphabet
    letters_only = re.sub('[^a-zA-Z]', ' ', raw_title)
    # Ignore case
    words = letters_only.lower().split()
    # Ignore insignificant words
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
def generate_model(X_train, X_test, y_train): # Multinomial Naive Bayes' Model
    """Train Naive Bayes model"""
    # Generate a blank multinomial naive bayes model
    naive_model = MultinomialNB()
    
    # Train the model
    classifier = naive_model.fit(X_train, y_train)
    
    return classifier

# --------------------------------------------------
def make_confusion_matrix(MNB_prediction, y_test, accuracy_per): # Multinomial Naive Bayes' Model
    """Plot confusion matrix"""
    MNB_confusion = confusion_matrix(MNB_prediction, y_test)
    plt.figure(figsize = (10,7))
    sn.heatmap(MNB_confusion, annot=True)
    plt.xlabel('Actual Class')
    plt.ylabel('Predicted Class')
    plt.title('Confusion Matrix \nAccuracy: {}%'.format(accuracy_per), size=14)
    plt.show()
 
# --------------------------------------------------
def write_test_data(test_out, y_test, model_prediction, raw_data): # Multinomial Naive Bayes' Model
    """Save data used for testing"""
    with open(test_out,'a') as fh:
            i = 0
            fh.write('Actual\tPredicted\tTitle\n')
            for ind, label in y_test.items():
                pred = model_prediction[i]
                tit = raw_data.title[ind]
                fh.write('{}\t{}\t{}\n'.format(label, pred, tit))
                i += 1
 
# -------------------------------------------------- 
def main():
    """The good stuff"""
    
    # Retrieve command-line arguments from argparse
    args = get_args()
    data_file = args.data
    pkl_file = args.out
    test_out = args.test_out
    split = args.test_split
    
    # Check for data file
    if not os.path.isfile(data_file):
        die('Data file "{}" not found.'.format(data_file))
    
    # Read in labeled data
    raw_data = pd.read_csv(data_file, delimiter='\t', header=0)
    
    # Extract title strings from data
    titles = []
    for i in range(raw_data.title.size):
        titles.append(clean_title(raw_data.title[i]))

    # Extract data labels
    y = raw_data.label
    
    # Split data between train and test
    t_train, t_test, y_train, y_test = train_test_split(titles, y, test_size=split)
    print('Extracting features')
    x_train, vectorizer = get_features(t_train, None)
    x_test, _ = get_features(t_test, vectorizer)
    
    print('Training model')
    model = generate_model(x_train, x_test, y_train)
    
    print('Testing model')
    model_prediction = model.predict(x_test)
    model_accuracy = model.score(x_test, y_test)
    accuracy_per = round(model_accuracy*1000)/10
    print('Model accuracy: {}%'.format(accuracy_per))
    
    print('Assessing confusion matrix')
    make_confusion_matrix(model_prediction, y_test, accuracy_per)    
    
    if os.path.isfile(test_out):
        os.remove(test_out)
        print('Removing previous test data file.')
    
    print('Saving test data.')
    write_test_data(test_out, y_test, model_prediction, raw_data)
    
    print('Saving pickle')
    pickle_tuple = (model, x_test, y_test, model_accuracy, vectorizer)
    with open(pkl_file, 'wb') as file:
        pickle.dump(pickle_tuple, file)
    
# --------------------------------------------------
if __name__ == '__main__':
    main()    