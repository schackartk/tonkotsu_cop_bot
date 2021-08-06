#!/usr/bin/env python3
"""
Author : schackartk
Purpose: A reddit bot for spreading awareness of the misspelling of 'tonkotsu'
Date   : 22 April 2020
"""

import argparse        # Get command line arguments
import bayes           # My model file
import config          # log in information file
import helpers as hp   # Custom made helpers
import logging         # Generate log of activity
import os              # Check for and delete files
import pickle          # Read pickled model file
import praw            # Interact with reddit
import re              # Regular expressions for post url
import time            # Time actions

from typing import NamedTuple


class Args(NamedTuple):
    """ Command-line arguments"""
    comment: str
    debug: bool
    deleted: str
    log: str
    model: str
    posts: str
    subs: str


# --------------------------------------------------
def get_args():
    """Get command-line arguments"""
    parser = argparse.ArgumentParser(
        description='Run the Tonkotsu Reddit Bot',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        '-c',
        '--comment',
        help='Bot comment string file',
        metavar='FILE',
        type=str,
        default='../data/comment.txt')

    parser.add_argument(
        '-D',
        '--Debug',
        help='Debugging flag',
        action='store_true')

    parser.add_argument(
        '-d',
        '--deleted',
        help='Deleted comments file',
        metavar='FILE',
        type=str,
        default='../data/deleted.txt')

    parser.add_argument(
        '-l',
        '--log',
        help='Log file',
        metavar='FILE',
        type=str,
        default='../data/.log')

    parser.add_argument(
        '-m',
        '--model',
        help='Model for classifying titles',
        metavar='PKL',
        type=str,
        default='../data/model.pkl')

    parser.add_argument(
        '-p',
        '--posts',
        help='Previously assesssed posts file',
        metavar='FILE',
        type=str,
        default='../data/id_file.txt')

    parser.add_argument(
        '-s',
        '--subreddits',
        help='List of subreddits to comment in',
        metavar='list',
        type=str,
        default='ramen,FoodPorn,test')

    args = parser.parse_args()

    return Args(comment=args.comment, debug=args.Debug,
                deleted=args.deleted, log=args.log,
                model=args.model, posts=args.posts,
                subs=args.subreddits)


# --------------------------------------------------
def get_history(id_file):
    """Get information on bot action history from file"""

    id_dict = {}

    # Make previously detected id_list from id_file contents
    with open(id_file, 'r') as fh:
        for line in fh.read().splitlines():
            if line:
                post_id, pred, _, _, _ = line.split('\t')
                id_dict[post_id] = pred

    return id_dict


# --------------------------------------------------
def get_comment(msg_file):
    """Get canned bot comment"""

    # Retrieve comment string from msg_file
    with open(msg_file)as fh:
        cmt = fh.read()

    return cmt


# --------------------------------------------------
def save_id(id_file, post_id, pred, act, sub, title):
    """Save ID of those scanned"""

    logging.debug(f'Saving ID\'s to "{id_file}"')

    # Save id and predicted classification to id_file
    with open(id_file, 'a') as fh:
        print(f'{post_id}\t{pred}\t{act}\t{sub}\t{title}',
              file=fh)

    logging.debug(f'ID\'s saved to "{id_file}"')


# --------------------------------------------------
def bot_login():
    """Sign bot into reddit"""

    # Give feedback on login process
    print('Logging in... ', end='')
    login_time = time.strftime('%Y/%m/%d %X')
    logging.info(f'{login_time}: Logging in.')

    # Sign into reddit with praw using config.py info
    r = praw.Reddit(username=config.username,
                    password=config.password,
                    client_id=config.client_id,
                    client_secret=config.client_secret,
                    user_agent='Tonkotsu Police v0.1')
    print('log in successful.')
    print(f'Logged in as {config.username}.')
    logging.debug('log in successful.')
    logging.debug(f'Logged in as {config.username}.')

    return r


# --------------------------------------------------
def predict(text, model_file):
    """Use previously trained model to classify title text"""

    # Unpickle Bayesian model file, made by bayes.py
    with open(model_file, 'rb') as file:
        model, x_test, y_test, model_accuracy, vec = pickle.load(file)

    # Check that model is importing okay
    if model_accuracy != model.score(x_test, y_test):
        hp.warn('Saved and test model accuracy do not match')

    # Get features from the text using old vectorizer
    text_features, _ = bayes.get_features([text], vec)

    # Get predicted classification using pickled model
    prediction = model.predict(text_features)

    return prediction


# --------------------------------------------------
def leave_comment(post, cmt_file):
    """leave bot comment"""

    cmt = get_comment(cmt_file)

    cmt_obj = post.reply(cmt)

    cmt = cmt.format(id=cmt_obj.fullname)
    cmt_obj.edit(cmt)


# --------------------------------------------------
def delete_comment(r, comment, del_file):
    """delete comment"""

    user_name = config.username

    if comment.author.name == user_name:
        comment.delete()
        msg = f'Comment removed: {comment.id}.'
        r.redditor(user_name).message('Comment Removed', msg)
    else:
        msg = f'Comment by {comment.author}'

    print(msg)
    logging.info(msg)
    with open(del_file, 'a') as fh:  # Record deleted commented id
        print(comment.id, file=fh)


# --------------------------------------------------
def react_to_post(post, pred, act, cmt_file, id_file):
    """save post info, comment if predicted mistake"""

    str1 = f'Model predicted {"in" if pred else ""}correct spelling.'
    str2 = f'{"C" if act else "Not c"}ommenting.'
    print(str1)
    print(f'{str2}..\n')
    logging.info(f'{str1} {str2}')

    sub = post.subreddit.display_name
    title = post.title

    save_id(id_file, post.id, pred, act, sub, title)

    if act:
        leave_comment(post, cmt_file)
        logging.info('Commented on post.')


# --------------------------------------------------
def react_to_summon(r, cmt_file, id_file, mention):
    """comment from summons"""

    summoner = mention.author
    sub = mention.subreddit.display_name
    parent_id = mention.parent_id
    post_id = parent_id[3:]

    print('Responding to summon.\n')
    logging.info('Responding to summon.')
    save_id(id_file, parent_id, 's', 1, sub, 'NA')
    save_id(id_file, post_id, 's', 'NA', sub, 'NA')

    if 't3_' in parent_id and sub != 'food':
        # respond to original post
        post_id = parent_id[3:]
        post = r.submission(id=post_id)
        leave_comment(post, cmt_file)
        logging.info('Commented on post.')
        mention.reply(f'Thank you /u/{summoner} for the tip!')
        logging.info('Commented on summoning')


# --------------------------------------------------
def investigate(r, cmt_file, id_file, model_file, subs):
    """Look for tonkotsu misspelling"""
    ct = 0  # Number of instances corrected

    user_name = config.username
    human_name = config.human_acct

    # Get previously assessed post id's
    id_dict = get_history(id_file)

    print('Scanning...\n')
    logging.info('Scanning posts...')

    # Collect newest 25 posts
    posts = r.subreddit('test+ramen+food+FoodPorn').new()

    # Iterate through posts
    for post in posts:

        post_title = post.title.lower()
        post_sub = post.subreddit.display_name

        # Check for string, make sure have not commented before
        if 'tonkatsu' in post_title and post.id not in id_dict.keys():
            print(f'Tonkatsu found in post: {post.id}.')
            print(f'Post title: "{post.title}".')
            logging.info(f'Tonktasu found in post: {post.id}.')
            logging.info(f'Post title: {post.title}')

            # Use Bayesian model to decide if should comment
            pred = int(predict(post_title, model_file))
            act = pred
            if pred:  # Decided to comment
                if post_sub in subs:
                    ct += 1  # Increase count for reporting
                    msg = 'Commented on post'
                else:
                    act = 0
                    msg = 'Predicted as incorrect, unauthorized sub'
            else:  # Decided not to comment
                msg = 'Post predicted as correct'

            react_to_post(post, pred, act, cmt_file, id_file)

            full_msg = f'{msg}: [{post.id}]({post.permalink})\n"{post.title}"'

            # Send messages notifying decision
            r.redditor(user_name).message('Tonkatsu Found', full_msg)
            r.redditor(human_name).message('Tonkatsu Found', full_msg)
            logging.info('Sent messages.')

            break  # Don't need to hit twice if "tonkatsu" is repeated

    print('Done scanning.')
    print(f'Commented on {ct} post{"" if ct == 1 else "s"}.\n')
    logging.info('Done scanning.')
    logging.info(f'Commented on {ct} post{"" if ct == 1 else "s"}.')


# --------------------------------------------------
def check_summons(r, cmt_file, id_file):
    """Check for username mentions / bot summons"""

    user_name = config.username
    human_name = config.human_acct

    print('Checking for summons...')
    logging.info('Checking for summons...')

    # Get previously commented on posts
    id_dict = get_history(id_file)

    # Get bot username mentions
    mentions = r.inbox.mentions()

    # Deal with username mentions
    for mention in mentions:

        parent_id = mention.parent_id  # Get the id of what was commented on
        post_id = parent_id[3:]  # Comments are prefaced with 't3_' or 't1_'

        # Check if this summon has been acted upon before
        if parent_id not in id_dict.keys():

            # Check if bot has commented on the post itself before
            if post_id in id_dict.keys():
                if id_dict[post_id] != 0:
                    break

            msg = 'Summon found'
            print(f'{msg}.')
            logging.info(f'{msg}.')
            react_to_summon(r, cmt_file, id_file, mention)

            # Post address, no comment info
            post_add = re.sub(r'[?]context=\d+', '', mention.context)
            full_msg = f'{msg}: [{mention.id}]({post_add})\n\n"{mention.body}"'

            # Send messages notifying decision
            r.redditor(user_name).message('Bot Summoned', full_msg)
            r.redditor(human_name).message('Bot Summoned', full_msg)
            logging.info('Sent messages.')

    print('Done checking for summons.\n')
    logging.info('Done checking for summons.')


# --------------------------------------------------
def purge(r, del_file):
    """Go through bot comments and delete downvoted ones"""

    user_name = config.username
    user = r.redditor(user_name)

    with open(del_file, 'r') as fh:
        deleted = fh.read().splitlines()

    print('Checking to purge comments... ')
    logging.info('Scanning bot comments...')

    # Go through bot's comments
    for comment in user.comments.new(limit=None):
        if comment.score < -1:
            delete_comment(r, comment, del_file)

    logging.info('Scanning PMs...')

    # Check PMs for requests to delete
    for message in r.inbox.messages():

        if message.subject != 'deletion':
            continue

        bad_cmt = r.comment(id=message.body)

        parent = bad_cmt.submission

        if bad_cmt.id in deleted:
            continue

        if parent.author == message.author:
            delete_comment(r, bad_cmt, del_file)

    print('Done purging.')
    logging.info('Done scanning comments.')


# --------------------------------------------------
def main():
    """The good stuff"""

    # Retrieve command-line arguments from argparse
    args = get_args()
    id_file = args.posts
    del_file = args.deleted
    log_file = args.log
    model_file = args.model
    cmt_file = args.comment
    sub_list = args.subs

    # Set up logging configurations, debug or just info
    logging.basicConfig(
        filename=log_file,
        filemode='a',
        level=logging.DEBUG if args.debug else logging.INFO
    )

    subs = sub_list.split(sep=",")

    # Check for files
    for f in [id_file, del_file, model_file, cmt_file]:
        if not os.path.isfile(f):
            hp.die(f'File: "{f}" not found')

    # Perform the real bot actions
    r = bot_login()  # Create a reddit instance via PRAW
    investigate(r, cmt_file, id_file, model_file, subs)
    check_summons(r, cmt_file, id_file)
    purge(r, del_file)
    logging.info('Logging off.\n')


# --------------------------------------------------
if __name__ == '__main__':
    main()
