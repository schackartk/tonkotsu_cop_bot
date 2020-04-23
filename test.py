"""
Author : schackartk
Purpose: Reddit bot tests
Date   : 22 April 2020
"""
from subprocess import getstatusoutput, getoutput
import os
import random
import re
import string
import bot
import pytest

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
    rv, out = getstatusoutput('{} -p {}'.format(prg, bad_file ))
    assert rv > 0
    assert out == 'No file "{}" found.'.format(bad_file)
    
    rv, out = getstatusoutput('{} -d {}'.format(prg, bad_file ))
    assert rv > 0
    assert out == 'No file "{}" found.'.format(bad_file)
    
def test_label():
    """label"""
    
    test = [('Nothing better than a good bowl of tonkatsu', True),
            ('I did it!!! I made Tonkatsu Chcachu Ramen!', True),
            ('Tonkatsu Ramen', True),
            ('Absolutely nailed my Tonkatsu. Finally!', True),
            ('Kakuni Tonkatsu Ramen', True),
            ('tonkatsu from hell - Samurai Noodles in Seattle', True),
            ('Spicy Tonkatsu Ramen from Atlanta, GA. Egg could\'ve used a bit more work but the broth was amazing', True),
            ('Tonkatsu ramen from Ramen-San in Chicago', True),
            ('Awesome pork tonkatcu ramen at Haiku Tokyo', True),
            ('Spicy Tonkatsu', True),
            ('Tonkatsu Black (ramen from my local ramen shop). Chashu, black fungus, green onions, egg, and garlic oil. Absolutely heavenly!', True),
            ('This is officially my favorite kind of ramen broth. Spicy tonkatsu. I got it level 3 spicy. The broth is so creamy and fatty.', True),
            ('Tonkatsu Tonkotsu ramen', False),
            ('Can we have a tonkatsu/tonkotsu correction-bot?', False),
            ('Tonkatsu vs. Tonkotsu - a Friendly PSA', False)
            ]