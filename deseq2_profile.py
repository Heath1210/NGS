#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
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
    This is designed to summarize DESeq2.sh file to generate DE gene counts and DE gene profile.

all.DE file (containing DE genesbetween fOocyte and M1, fOocyte and M2)

ENSG00000242071 fOocyte._vs_.M1_up
ENSG00000228929 fOocyte._vs_.M1_up
ENSG00000213553 fOocyte._vs_.M1_up
ENSG00000224411 fOocyte._vs_.M1_up
ENSG00000242071 fOocyte._vs_.M2_up
ENSG00000228929 fOocyte._vs_.M2_up
ENSG00000213553 fOocyte._vs_.M2_up
ENSG00000224411 fOocyte._vs_.M2_up
ENSG00000242071 M1._vs_.fOocyte_up
ENSG00000228929 M1._vs_.fOocyte_up
ENSG00000213553 M1._vs_.fOocyte_up
ENSG00000224411 M1._vs_.fOocyte_up
ENSG00000242071 M2._vs_.fOocyte_up
ENSG00000228929 M2._vs_.fOocyte_up
ENSG00000213553 M2._vs_.fOocyte_up
ENSG00000224411 M2._vs_.fOocyte_up

'''

import sys
import os
from json import dumps as json_dumps
from time import localtime, strftime 
timeformat = "%Y-%m-%d %H:%M:%S"
from optparse import OptionParser as OP
#from multiprocessing.dummy import Pool as ThreadPool
import re
from tools import *
from json import load as json_load
import pandas as pd

#from bs4 import BeautifulSoup
reload(sys)
sys.setdefaultencoding('utf8')

debug = 0

def plot_de_count(all_DE, condL, type):
    count = all_DE+'.count.xls'
    count_fh = open(count, 'w')
    countD = {}
    for line in open(all_DE):
        type = line.split()[1]
        firstSep  = type.find('._')
        secondSep = type.find('_.')
        
        condA = type[:firstSep]
        #condB, cmp = type[secondSep+2:].rsplit('_', 1)
        condB = type[secondSep+2:]
        cmp = type[firstSep+2:secondSep]
        #if cmp == 'up':
        if cmp == 'higherThan':
            condA, condB = condB, condA
        else:
            #assert cmp == 'dw', cmp
            assert cmp == 'lowerThan', cmp
        if condA not in countD:
            countD[condA] = {}
        if condB not in countD[condA]:
            countD[condA][condB] = 0
        countD[condA][condB] += 1
    #---------------------------------
    print >>count_fh, 'Samp\t'+'\t'.join(condL)
    for cond in condL:
        subD = countD.get(cond, {})
        tmpL = [str(subD.get(sec_cond, 'NA')) for sec_cond in condL]
        print >>count_fh, "{}\t{}".format(cond, '\t'.join(tmpL))
    count_fh.close()
    ## In this heatmap, each colored block represents 
    ## number of up-regulated DE genes or regions in samples in X-axis
    ## compared to samples in Y-axis.
    cmd = ["s-plot heatmapS -f", count, "-A 45 -T 2 -l top -I DE_gene_count",
          "-b TRUE -Y white"]
    os.system(' '.join(cmd))
#-----------------plot_de_count-------------
def plot_de_profile(all_DE, norm_mat, condL):
    #Extract DE_profile
    all_DE_idL = list(set([line.split()[0] for line in open(all_DE)]))
    if len(all_DE_idL) < 1:
        return
    de_norm_mat = norm_mat[norm_mat.index.isin(all_DE_idL)]
    de_norm_mat_f = all_DE + '.norm' 
    de_norm_mat.index.name = 'ID'
    de_norm_mat.to_csv(de_norm_mat_f, sep=b"\t")
    #Plot
    cmd = ['s-plot prettyHeatmap -f', de_norm_mat_f, '-c', str(len(condL))]
    os.system(' '.join(cmd))
#-------------plot_de_profile-----------------

def cmdparameter(argv):
    if len(argv) == 1:
        global desc
        print >>sys.stderr, desc
        cmd = 'python ' + argv[0] + ' -h'
        os.system(cmd)
        sys.exit(1)
    usages = "\n\t%prog -i all.DE -c compare_pair -m DESeq2.normalized.xls"
    parser = OP(usage=usages)
    parser.add_option("-i", "--all-DE", dest="all_de",
        help=".all.DE file generated by DESeq2.sh")
    parser.add_option("-c", "--compare-pair", dest="filein",
        help="compare_pair given to DESeq2.sh.")
    parser.add_option("-m", "--norm-matrix", dest="norm_mat",
        help="Normalized data matrix file which will be used for \
 DE profile analysis.")
    parser.add_option("-v", "--verbose", dest="verbose",
        default=0, help="Show process information")
    parser.add_option("-D", "--debug", dest="debug",
        default=False, help="Debug the program")
    (options, args) = parser.parse_args(argv[1:])
    assert options.all_de != None, "A filename needed for -i"
    return (options, args)
#--------------------------------------------------------------------

def main():
    options, args = cmdparameter(sys.argv)
    #-----------------------------------
    compare_pair = options.filein
    norm_mat_fl  = options.norm_mat
    all_DE       = options.all_de
    global debug
    verbose      = options.verbose
    debug        = options.debug
    #-----------------------------------
    condL = list(set([i for line in open(compare_pair) for i in line.split()]))
    condL.sort()

    plot_de_count(all_DE, condL, 'gene')

    norm_mat = pd.read_table(norm_mat_fl, header=0, index_col=0)
    norm_mat.index.name = 'ID'
    plot_de_profile(all_DE, norm_mat, condL)

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
    ###---------procompare_pair the program---------
    #import procompare_pair
    #procompare_pair_output = sys.argv[0]+".prof.txt")
    #procompare_pair.run("main()", profile_output)
    #import pstats
    #p = pstats.Stats(procompare_pair_output)
    #p.sort_stats("time").print_stats()
    ###---------procompare_pair the program---------


