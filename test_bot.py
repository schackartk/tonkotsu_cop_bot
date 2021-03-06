"""
Author : schackartk
Purpose: Reddit bot tests
Date   : 22 April 2020
"""

"""
Run using python3 -m pytest -v test_bot.py
"""

import bot    # My bot program, to be tested
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
    """bad input for required file names"""
    
    bad_file = random_string()
    
    for arg_flag in ['c', 'd', 'p', 'm']:
        rv, out = getstatusoutput('{} -{} {}'.format(prg, arg_flag, bad_file))
        assert rv > 0
        assert out == 'File: "{}" not found'.format(bad_file)
    
# --------------------------------------------------
def test_get_history():
    """retrieve previously analyzed post id's"""
    
    id_file = 'data/id_file.txt'
    id_dict = bot.get_history(id_file)
    
    assert str(type(id_dict)) == "<class 'dict'>"
    
# --------------------------------------------------
def test_config():
    """check attributes in config.py"""
    
    # Assumption is made in bot.py that config.py exists in same directory
    assert os.path.isfile('config.py')
    
    import config # Login config file
    
    # Attributes assumed to be present in config.py
    attr_list = ['username',
                 'password',
                 'client_id',
                 'client_secret',
                 'human_acct']
    
    # Check that imported config.py has those attributes
    for attr in attr_list:
        assert hasattr(config, attr)

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
    posts = r.subreddit('test').new()
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

# --------------------------------------------------
def test_runs_defaults():
    """no errors when running with defaults"""
    # This high-level test is useful to me, but is quite fragile.
    # If a required file such as the model is not present, it will fail.
    
    rv, out = getstatusoutput('{} -s test'.format(prg))
    assert rv == 0