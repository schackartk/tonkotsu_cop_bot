"""
Author : schackartk
Purpose: A reddit bot for spreading awareness of the misspelling of 'tonkotsu'
Date   : 22 April 2020
"""

import argparse  # Get command line arguments
import bayes     # My model file
import config    # log in information file
import os        # Check for and delete files
import pickle    # Read pickled model file
import praw      # Interact with reddit
import sys       # Handle errors
import time      # Time actions

# --------------------------------------------------
def get_args():
    """Get command-line arguments"""
    parser = argparse.ArgumentParser(
        description='Run the Tonkotsu Police Bot',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    
    parser.add_argument(
        '-p',
        '--posts',
        help='Previously commented posts file',
        metavar='FILE',
        type=str,
        default='data/id_file.txt')
    
    parser.add_argument(
        '-d',
        '--deleted',
        help='Deleted comments file',
        metavar='FILE',
        type=str,
        default='data/deleted.txt')
    
    parser.add_argument(
        '-m',
        '--model',
        help='Model for classifying titles',
        metavar='PKL',
        type=str,
        default='data/model.pkl')
    
    parser.add_argument(
        '-l',
        '--login',
        help='Log in information file',
        metavar='FILE',
        type=str,
        default='data/config.py')

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
def get_history(id_file, del_file):
    
    """Get information on bot action history from files"""
    id_list = []
    del_list = []
        
    with open(id_file, 'r') as fh:
        for line in fh.read().splitlines():
            id_list.append(line)
   
    with open(del_file, 'r') as fh:
        for line in fh.read().splitlines():
            del_list.append(line)
            
    history = {'post_id': id_list, 'deleted': del_list}
        
    return history

# --------------------------------------------------
def get_comment():
    """Get canned bot comment"""

    cmt = "^(Beep boop, I am a robot)\n\nDid you happen to mean [tonkotsu](https://en.wikipedia.org/wiki/Tonkotsu_ramen) instead of [tonkatsu](https://en.wikipedia.org/wiki/Tonkatsu)?\n\n^(I am a reddit bot that has been trained to distinguish when usage of 'tonkatsu' is a mistake, but I make mistakes myself. If this is indeed *tonkatsu*, please downvote this comment. With enough downvotes, it will be automatically deleted.)"
    
    return cmt

# --------------------------------------------------
def bot_login():
    """Sign bot into reddit"""
    
    print('Logging in... ', end='')
    r = praw.Reddit(username = config.username,
                password = config.password,
                client_id = config.client_id,
                client_secret = config.client_secret,
                user_agent = 'Tonkotsu Police v0.1')
    
    print('log in successful.')
    print('Logged in as {}.'.format(config.username))
    return r

# --------------------------------------------------
def predict(text, model_file):
    """Use previously trained model to classify title text"""
    
    # Unpickle Bayesian model file, made by bayes.py
    with open(model_file, 'rb') as file:
        model, x_test, y_test, model_accuracy, vec = pickle.load(file)
    
    # Check that model is importing okay
    if model_accuracy != model.score(x_test, y_test):
        warn('Saved and test model accuracy do not match')
    
    # Get features from the text using old vectorizer
    text_features, _ = bayes.get_features([text], vec)
    
    # Get predicted classification using pickled model
    prediction = model.predict(text_features)
    
    return prediction

# --------------------------------------------------
def investigate(r, history, id_file, model_file):
    """Look for tonkotsu misspelling"""
    ct = 0 # Number of instances corrected
    
    cmt = get_comment()
    
    print('Scanning...\n')
    posts = r.subreddit('test').new(limit=25)
    for post in posts:
        
        post_title = post.title.lower()
        
        if 'tonkatsu' in post_title and post.id not in history['post_id']: 
            print('Tonkatsu found in post: {}.'.format(post.id))
            print('Post title: {}'.format(post.title))
            
            if int(predict(post_title, model_file)):
                print('Model predicted mistake spelling')
                print('Commenting\n')
                # Check if user corrected it
                ct += 1
                with open(id_file, 'a') as fh:
                    print(post.id, file=fh)
                post.reply(cmt)
                # Need to add in message bot's acct
            else:
                print('Model predicted correct spelling')
                print('Not commenting\n')
                # Need to add in message bot's acct
            
    print('Done scanning.')
    print('Commented on {} post{}\n'.format(ct, '' if ct == 1 else 's'))

# --------------------------------------------------
def purge(r, history, del_file):
    """Go through bot comments and delete downvoted ones"""
    user_name = config.username
    user = r.redditor(user_name)
    
    print('Checking to purge comments... ')
    for comment in user.comments.new(limit=None):
        if comment.score < -1 and comment.id not in history['deleted']:
            comment.delete()
            msg = 'Comment removed due to downvotes: {}'.format(comment.id)
            r.redditor(user_name).message('Comment Removed', msg)
            print(msg)
            with open(del_file, 'a') as fh:
                print(comment.id, file=fh)
       
    print('Done purging.')
    
# --------------------------------------------------
def main():
    """The good stuff""" 
    
    # Retrieve command-line arguments from argparse
    args = get_args()
    id_file = args.posts
    del_file = args.deleted
    model_file = args.model
    
    # Check for files
    for f in [id_file, del_file, model_file]:
        if not os.path.isfile(f):
            die('File: "{}" not found'.format(f))
    
    # Get history from files
    # Make 'history' dictionary with keys: post_id, deleted
    history = get_history(id_file, del_file)
      
    # Log in to reddit
    r = bot_login()
    
#    while True:
#        try:        
    investigate(r, history, id_file, model_file)
    purge(r, history, del_file)
#    time.sleep(30)
#        except:
#            print('Resuming in 10 seconds...')
#            time.sleep(10)
    
# --------------------------------------------------
if __name__ == '__main__':
    main()    