"""
Author : schackartk
Purpose: Reddit bot tests
Date   : 22 April 2020
"""

"""
Run using python3 -m pytest -v test_bot.py
"""

import bot
import os
import pytest
import random
import re
import string

from subprocess import getstatusoutput, getoutput

prg = "python3 bot.py"

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

        
    
           