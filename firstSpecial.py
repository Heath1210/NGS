#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''


Copyright 2010, 陈同 (chentong_biology@163.com).  
Please see the license file for legal information.
===========================================================
'''
__version__ = '0.1'
__revision__ = '0.1'
__author__ = 'chentong & ct586[9]'
__author_email__ = 'chentong_biology@163.com'
#=========================================================
#from __future__ import division, with_statement
import sys

def main():
    if len(sys.argv) != 3:
        print >>sys.stderr, 'Find the locus only in the first file.'
        print >>sys.stderr, 'Using python %s filename1 filename2' % sys.argv[0]
        sys.exit(0)
    aDict = {}
    for line in open(sys.argv[2]):
        line = line.strip()
        aDict[line] = ''
    sys.stdout.writelines([line for line in open(sys.argv[1]) \
            if line.strip() not in aDict])

if __name__ == '__main__':
    main()

