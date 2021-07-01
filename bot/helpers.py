#!/usr/bin/env python3
"""
Author : schackartk
Purpose: Simple helper functions for bot
Date   : 1 July 2021
"""

import sys

# --------------------------------------------------
def warn(msg):
    """Print a message to STDERR"""
    print(msg, file=sys.stderr)


# --------------------------------------------------
def die(msg='Something bad happened'):
    """warn() and exit with error"""
    warn(msg)
    sys.exit(1)