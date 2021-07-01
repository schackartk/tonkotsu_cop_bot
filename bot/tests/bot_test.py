"""
Author : schackartk
Purpose: Reddit bot tests
Date   : 22 April 2020
"""

import bot            # My bot program, to be tested
import helpers as hp  # Custom helpers
import config         # Login config file
import os             # Check for files
import re             # Regular expressions

from subprocess import getstatusoutput

PRG = "./bot.py"


# --------------------------------------------------
def test_exists():
    """ Program bot.py exists """

    assert os.path.isfile(PRG)


# --------------------------------------------------
def test_usage():
    """ bot.py usage """

    for flag in ['-h', '--help']:
        rv, out = getstatusoutput(f'{PRG} {flag}')
        assert rv == 0
        assert re.match("usage", out, re.IGNORECASE)

    rv, out = getstatusoutput(f'{PRG} fox.txt')
    assert rv > 0
    assert re.match("usage", out, re.IGNORECASE)


# --------------------------------------------------
def test_bad_input():
    """ Bad input for required file names """

    bad_file = hp.random_string()

    for arg_flag in ['c', 'd', 'p', 'm']:
        rv, out = getstatusoutput(f'{PRG} -{arg_flag} {bad_file}')
        assert rv > 0
        assert out == f'File: "{bad_file}" not found'


# --------------------------------------------------
def test_get_history():
    """ Retrieve previously analyzed post id's """

    id_file = '../data/id_file.txt'
    id_dict = bot.get_history(id_file)

    assert str(type(id_dict)) == "<class 'dict'>"


# --------------------------------------------------
def test_config():
    """ Check attributes in config.py """

    # Assumption is made in bot.py that config.py exists in same directory
    assert os.path.isfile('config.py')

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
    """ Check ability to log in to reddit """

    reddit_instance = bot.bot_login()
    assert str(type(reddit_instance)) == "<class 'praw.reddit.Reddit'>"


# --------------------------------------------------
def test_post_ret():
    """ Check ability to retrieve posts """

    post_type = "<class 'praw.models.listing.generator.ListingGenerator'>"

    r = bot.bot_login()
    posts = r.subreddit('test').new()
    assert str(type(posts)) == post_type


# --------------------------------------------------
def test_predict():
    """ See if prediction model is behaving the same """

    with open('../data/test_data.txt', 'r') as f:
        next(f)  # Skip header row
        for line in f:
            fields = line.split('\t')
            old_pred = int(fields[1])
            title = fields[2]
            new_pred = int(bot.predict(title, '../data/model.pkl'))
            assert new_pred == old_pred


# --------------------------------------------------
def test_runs_defaults():
    """ No errors when running with defaults """
    # This high-level test is useful to me, but is quite fragile.
    # If a required file such as the model is not present, it will fail.

    rv, _ = getstatusoutput(f'{PRG} -s test')
    assert rv == 0
