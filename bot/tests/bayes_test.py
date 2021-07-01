"""
Author : schackartk
Purpose: Reddit bot model learning tests
Date   : 1 July 2021
"""

import helpers as hp  # Custom helpers
import os             # Check for files
import re             # Regular expressions
import shutil

from subprocess import getstatusoutput

PRG = './bayes.py'


# --------------------------------------------------
def test_exists():
    """ bayes.py exists """

    assert os.path.isfile(PRG)


# --------------------------------------------------
def test_usage():
    """ bayes.py usage """

    for flag in ['-h', '--help']:
        rv, out = getstatusoutput(f'{PRG} {flag}')
        assert rv == 0
        assert re.match("usage", out, re.IGNORECASE)


# --------------------------------------------------
def test_bad_input():
    """ Bad input for required file"""

    bad_file = hp.random_string()

    rv, out = getstatusoutput(f'{PRG} -d {bad_file}')
    assert rv > 0
    assert out == f'Data file "{bad_file}" not found.'


# --------------------------------------------------
def test_runs_okay():
    """ Runs on good input """

    out_dir = 'out_test'
    try:
        if os.path.isdir(out_dir):
            shutil.rmtree(out_dir)

        os.makedirs(out_dir)

        rv, _ = getstatusoutput(f'{PRG} -o {out_dir}/model.pkl '
                                f'-t {out_dir}/test_data.txt')

        assert rv == 0

        assert os.path.isfile(f'{out_dir}/model.pkl')
        assert os.path.isfile(f'{out_dir}/test_data.txt')

    finally:
        if os.path.isdir(out_dir):
            shutil.rmtree(out_dir)
