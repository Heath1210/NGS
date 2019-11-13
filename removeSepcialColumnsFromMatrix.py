#!/usr/bin/env python
# -*- coding: utf-8 -*-
#from __future__ import unicode_literals
from __future__ import division, with_statement
'''
Copyright 2015, 陈同 (chentong_biology@163.com).  
===========================================================
'''
__author__ = 'chentong & ct586[9]'
__author_email__ = 'chentong_biology@163.com'
#=========================================================
desc = '''
Program description:
    This is designed to paste multiple files using pandas.
'''

import sys
import os
from json import dumps as json_dumps
from time import localtime, strftime 
timeformat = "%Y-%m-%d %H:%M:%S"
from optparse import OptionParser as OP
import pandas as pd
import re
#from multiprocessing.dummy import Pool as ThreadPool

#from bs4 import BeautifulSoup
#reload(sys)
#sys.setdefaultencoding('utf8')

debug = 0

def fprint(content):
    """ 
    This is a Google style docs.

    Args:
        param1(str): this is the first param
        param2(int, optional): this is a second param
            
    Returns:
        bool: This is a description of what is returned
            
    Raises:
        KeyError: raises an exception))
    """
    print json_dumps(content,indent=1)

def cmdparameter(argv):
    if len(argv) == 1:
        global desc
        print >>sys.stderr, desc
        cmd = 'python ' + argv[0] + ' -h'
        os.system(cmd)
        sys.exit(1)
    usages = "%prog -i file"
    parser = OP(usage=usages)
    parser.add_option("-i", "--input-file", dest="filein",
        metavar="FILEIN", help="A numerical matrix file")
    parser.add_option("-S", "--skip-col", dest="skip_col",
        metavar="SKIP_COL", 
        help="A file with one column containing names of columns to be removed.")
    parser.add_option("-H", "--header", dest="header",
        default=0, type='int', help="An integer to specify the header line. Default <O> represents using first line as header line. Give <-1> to specify no header line." )
    parser.add_option("-r", "--index-col", dest="index_col",
        default='0', help="Column to use as the row labels of the DataFrame (Default 0 represents the first column). If a sequence like <0,1,2> is given, a MultiIndex will be used. Supply <None> to turn off index_col.")
    parser.add_option("-c", "--usecols", dest="usecols",
        default="None", help="Return a subset of the columns. All elements in this array must either \
be positional (i.e. integer indices into the document columns) or strings \
that correspond to column names provided either by the user in `names` or \
inferred from the document header row(s). For example,  a valid `usecols` \
parameter would be <0,1,2> or <foo,bar,baz>. Using this parameter \
results in much faster parsing time and lower memory usage. \
*******One important note, <index_col> should be also included in <usecols>. \
Default <None> to read in all columns.")
    #parser.add_option("-n", "--rename_cols", dest="rename_cols",
    #    default="infer", help="Rename columns before merging. If only one column is \
#extracted (excluding row index), column name will be renamed with <file_label>; \
#If more than one columns are extracted, column names will be renamed with <file_label_original_name>. \
#If a list of names are given when extracting multiple columns, \
#column names will be renamed with <file_label_given_name>.\
#Supply <None> to disable rename.")
    parser.add_option("-o", "--outputfile", dest="output",
        help="Output file.")
    parser.add_option("-v", "--verbose", dest="verbose",
        action="store_true", help="Show process information")
    parser.add_option("-D", "--debug", dest="debug",
        default=False, action="store_true", help="Debug the program")
    (options, args) = parser.parse_args(argv[1:])
    assert options.filein != None, "A filename needed for -i"
    return (options, args)
#--------------------------------------------------------------------


def main():
    options, args = cmdparameter(sys.argv)
    #-----------------------------------
    file = options.filein
    skip_col = options.skip_col
    skip_colL = [line.strip() for line in open(skip_col)]
    #fileL = re.split(r'[, ]*', file.strip())
    #if options.rename_cols != "None":
    #    label = options.label
    #    labelL = re.split(r'[, ]*', label.strip())
    #else:
    #    labelL = fileL
    header = options.header
    if header == -1:
        header = 'None'
    index_col = options.index_col.strip()
    if index_col != "None":
        index_col = [int(i) for i in re.split(r'[, ]*', index_col)]
    else:
        index_col = None
    #-----------------------------------------------------
    usecols = options.usecols
    #print >>sys.stderr, usecols
    if usecols != "None":
        usecols = usecols.split(',')
        usecols_2 = [int(i) for i in usecols if i.isdigit()]
        if len(usecols_2) == len(usecols):
            usecols = usecols_2
    else:
        usecols = None
    #print >>sys.stderr, usecols
    #---------------------------------------------------------
    #rename_cols = options.rename_cols
    #if rename_cols not in ["infer", "None"]:
    #    rename_cols = re.split(r'[, ]*', rename_cols.strip())
    #methodD = {"mad":1,"std":1,"mean":1,"sum":1,"median":1,
    #        "min":1,"max":1,"var":1,"skew":1,"kurt":1}
    #method = options.method
    #assert method, "-m/--method is missing"
    #methods = re.split(r'[, ]*', method.strip())
    #for i in methods:
    #    assert i in methodD, sys.exit("Un-supproted method "+i)
    #--------------------
    #sort_values = options.sort_values
    #if sort_values:
    #    sort_values = re.split(r'[, ]*', sort_values.strip())
    #else:
    #    sort_values = methods
    #--------------------------------------------------
    #ascending = options.ascending
    #uncompressed = options.uncompressed
    #if not options.output:
    #    suffix = ['xls', 'tsv', 'csv', 'txt']
    #    if file.find('.') != -1:
    #        file_name, suf = file.rsplit('.', 1)
    #        if suf not in suffix:
    #            file_name = file
    #    else:
    #        file_name = file
    #    output = file_name
    #else:
    output = options.output
    assert output, "-o/--outputfile should be supplied."
    #output += '.' + '_'.join(methods)
    verbose = options.verbose
    #top = options.top
    global debug
    debug = options.debug
    #-----------------------------------
    matrix = pd.read_table(file, header=header, index_col=index_col, usecols=usecols)
    matrix = matrix.drop(skip_colL, axis=1)
    matrix.to_csv(output, sep=b"\t")
    ###--------multi-process------------------
    #pool = ThreadPool(5) # 5 represents thread_num
    #result = pool.map(func, iterable_object)
    #pool.close()
    #pool.join()
    ###--------multi-process------------------
    if verbose:
        print >>sys.stderr,\
            "--Successful %s" % strftime(timeformat, localtime())

if __name__ == '__main__':
    startTime = strftime(timeformat, localtime())
    main()
    endTime = strftime(timeformat, localtime())
    fh = open('python.log', 'a')
    print >>fh, "%s\n\tRun time : %s - %s " % \
        (' '.join(sys.argv), startTime, endTime)
    fh.close()
    ###---------profile the program---------
    #import profile
    #profile_output = sys.argv[0]+".prof.txt")
    #profile.run("main()", profile_output)
    #import pstats
    #p = pstats.Stats(profile_output)
    #p.sort_stats("time").print_stats()
    ###---------profile the program---------


