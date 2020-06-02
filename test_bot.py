"""
Author : schackartk
Purpose: Reddit bot tests
Date   : 22 April 2020
"""

"""
Run using python3 -m pytest -v test_bot.py
"""

import bot    # My bot program, to be tested
import config # Login config file
import os     # Check for files
import pytest # Testing
import random # Generate random string
import re     # Regular expressions
import string # strings?

from subprocess import getstatusoutput, getoutput

prg = "python bot.py"

# --------------------------------------------------
def random_string():
    """generate a random filename"""

    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))

# --------------------------------------------------
def test_usage():
    """usage"""
    rv1, out1 = getstatusoutput('{} -h'.format(prg))
    assert rv1 == 0
    assert re.match("usage", out1, re.IGNORECASE)

    rv2, out2 = getstatusoutput('{} fox.txt'.format(prg))
    assert rv2 > 0
    assert re.match("usage", out2, re.IGNORECASE)
    
# --------------------------------------------------
def test_bad_input():
    """bad input"""
    
    bad_file = random_string()
    rv, out = getstatusoutput('{} -c {}'.format(prg, bad_file ))
    assert rv > 0
    assert out == 'File: "{}" not found'.format(bad_file)
    
    rv, out = getstatusoutput('{} -d {}'.format(prg, bad_file ))
    assert rv > 0
    assert out == 'File: "{}" not found'.format(bad_file)
    
    rv, out = getstatusoutput('{} -p {}'.format(prg, bad_file ))
    assert rv > 0
    assert out == 'File: "{}" not found'.format(bad_file)
    
# --------------------------------------------------
def test_get_history():
    """retrieve previously analyzed post id's"""
    
    id_file = 'data/id_file.txt'
    id_list = bot.get_history(id_file)
    
    assert str(type(id_list)) == "<class 'dict'>"
    
# --------------------------------------------------
def test_login():
    """check ability to log in to reddit"""
    
    reddit_instance = bot.bot_login()
    assert str(type(reddit_instance)) == "<class 'praw.reddit.Reddit'>"
    
# --------------------------------------------------
def test_post_ret():
    """check ability to retrieve posts"""
    
    post_type = "<class 'praw.models.listing.generator.ListingGenerator'>"
    
    r = bot.bot_login()
    posts = r.subreddit('test+ramen+food+foodporn').new()
    assert str(type(posts)) == post_type
    
# --------------------------------------------------
def test_predict():
    """see if prediction model is behaving the same"""
    with open('data/test_data.txt', 'r') as f:
        next(f) # Skip header row
        for line in f:
            fields = line.split('\t')
            old_pred = int(fields[1])
            title = fields[2]
            new_pred = int(bot.predict(title,'data/model.pkl'))
            assert new_pred == old_pred