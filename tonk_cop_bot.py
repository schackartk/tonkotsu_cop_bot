"""
Author : kschackart
Purpose: A reddit bot for spreading awareness of the misspelling of 'tonkotsu'
Date   : 22 April 2020
"""
import argparse
import config # log in information file
import os
import praw
import re
import sys
import time

# --------------------------------------------------
def get_args():
    """get command-line arguments"""
    parser = argparse.ArgumentParser(
        description='Run the Tonkotsu Police Bot',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        '-p',
        '--posts',
        help='Previously commented posts file',
        metavar='FILE',
        type=str,
        default='id_file.txt')
    
    parser.add_argument(
            '-d',
            '--deleted',
            help='Deleted comments file',
            metavar='FILE',
            type=str,
            default='deleted.txt')

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
    id_list = []
    del_list = []
    
    for file in [id_file, del_file]:
        if not os.path.isfile(file):
            die('No file "{}" found.'.format(file))
        
    with open(id_file, 'r') as fh:
        for line in fh.read().splitlines():
            id_list.append(line)
   
    with open(del_file, 'r') as fh:
        for line in fh.read().splitlines():
            del_list.append(line)
            
    history = {'post_id': id_list, 'deleted': del_list}
        
    return history

# --------------------------------------------------
def bot_login():
    
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
def investigate(r, history, id_file):
    katsu_count = 0
    
    print('Scanning... ')
    posts = r.subreddit('test').new(limit=25)
    for post in posts:
        if 'tonkatsu' in post.title and post.id not in history['post_id']:
            print('Tonkatsu found in post: {}.'.format(post.id))
            katsu_count += 1
            with open(id_file, 'a') as fh:
                print(post.id, file=fh)
            post.reply('Tonkatsu found!')
            
    print('Done scanning.')
    print('Commented on {} posts'.format(katsu_count))

# --------------------------------------------------
def purge(r, history, del_file):
    user_name = config.username
    user = r.redditor(user_name)
    
    print('Checking to purge... ')
    for comment in user.comments.new():
        print('Comment score: {}'.format(comment.score))
        if comment.score < -1 and comment.id not in history['deleted']:
            comment.delete()
            msg = 'Comment removed due to downvotes: {}.format'(comment.id)
            r.redditor(user_name).message('Comment Removed', msg)
            print(msg)
            with open(del_file, 'a') as fh:
                print(comment.id, file=fh)
    
    print('Done purging.')
# --------------------------------------------------
def main():
    """All the stuff"""    
    args = get_args()
    id_file = args.posts
    del_file = args.deleted
    
    history = get_history(id_file, del_file)
      
    r = bot_login()
    
#    while True:
#        try:        
    investigate(r, history, id_file)
    purge(r, history, del_file)
#    time.sleep(30)
#        except:
#            print('Resuming in 10 seconds...')
#            time.sleep(10)
    
# --------------------------------------------------
if __name__ == '__main__':
    main()    