#!/usr/bin/env python
# -*- coding: utf-8 -*-
#from __future__ import division, with_statement
'''
Copyright 2010, 陈同 (chentong_biology@163.com).  
Please see the license file for legal information.
===========================================================
'''
__author__ = 'chentong & ct586[9]'
__author_email__ = 'chentong_biology@163.com'
#=========================================================

desc = "\nThis is designed to sort clusters to get beautiful output.\n"

def sortFunc(x, index):
    xl = x.split('\t')
    sum = 0
    for i in index:
        sum += float(xl[int(i)])
    return sum
#-----------------------------------------------------------

import sys
import os
from json import dumps as json_dumps
from time import localtime, strftime 
timeformat = "%Y-%m-%d %H:%M:%S"
from optparse import OptionParser as OP
#from multiprocessing.dummy import Pool as ThreadPool
import numpy as np

debug = 0

def fprint(content):
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
        metavar="FILEIN", 
        help="The output of s-plot heatmapS or kmeans.test.sh. \
Generally a data matrix with the first column as rownames and \
the last column as cluster info is acceptable.")
    parser.add_option("-s", "--sampleGroup", dest="sampleGroup",
        help="sampleGroup file with first line as header line, first column as sample names and second columns as group information.")
    parser.add_option("-v", "--verbose", dest="verbose",
        default=0, help="Show process information")
    parser.add_option("-d", "--debug", dest="debug",
        default=False, help="Debug the program")
    (options, args) = parser.parse_args(argv[1:])
    assert options.filein != None, "A filename needed for -i"
    return (options, args)
#--------------------------------------------------------------------

def determineClusterSort(file, sampleGroupD={}, header=1):
    aDict = {}
    for line in open(file):
        if header:
            header -= 1
            continue
        #---------------------
        lineL = line.split()
        clu = lineL[-1]
        dataL = [float(i) for i in lineL[1:-1]]
        if clu not in aDict:
            aDict[clu] = []
        aDict[clu].append(dataL)
    #------------------------------------
    bDict = {}
    for clu, array in aDict.items():
        if debug:
            print >>sys.stderr, "Cluster: " +clu
        array = np.array(array)
        #if debug:
        #    print >>sys.stderr,  array
        array = np.average(array, axis=0)
        if debug:
            print >>sys.stderr, ">Average:"
            print >>sys.stderr,  array
        maxL = []
        # 获取并存储最大值、次大值。。。最小值所在的列
        while len(maxL) < len(array):
            max = np.argmax(array)
            maxL.append(max)
            array[max] = min(array) - 1
        #array = np.argsort(array)
        #print array
        if debug:
            print >>sys.stderr, ">maxL:"
            print >>sys.stderr, maxL
            #print >>sys.stderr, ">After Max:"
            #print >>sys.stderr,  array
        bDict[clu] = maxL
    #----------------------------------
    cluL = bDict.keys()
    if debug:
        print >>sys.stderr, bDict
    #获取cluster顺序，成对角线排列
    # 最大值所在的列越靠后的，cluster排位越靠后
    # 最大值所在的列越靠前的，cluster优先输出
    cluL.sort(key=lambda x: list(bDict[x]), reverse=True)
    # Cluster内部按最大值所在列排序
    # sortL = [bDict[x][0]+1 for x in cluL]
    #sortL = [sampleGroupD[bDict[x][0]+1] for x in cluL]
    sortL = [sampleGroupD.get(bDict[x][0]+1, [bDict[x][0]+1]) for x in cluL]
    if debug:
        print >>sys.stderr, cluL
        print >>sys.stderr, sortL
    return cluL, sortL
#-----------------------------------
def sampleGroupDetermine(file, sampleGroup):
    headerD = {}
    for line in open(file):
        j = 1
        for i in line.strip().split('\t')[1:-1]:
            headerD[i] = j
            headerD[j] = i
            j += 1
        break
    #-------------------------------
    header = 1
    sgD = {}
    for line in open(sampleGroup):
        if header:
            header -= 1 
            continue
        #--------------------
        sample, grp = line.split()
        sgD[sample] = grp
        if grp not in sgD:
            sgD[grp] = []
        sgD[grp].append(headerD[sample])
    #---------------------------
    sampleGroupD = {}
    for i in range(1, j):
        sampleGroupD[i] = sgD[sgD[headerD[i]]]
    if debug:
        print >>sys.stderr, sampleGroupD
    return sampleGroupD
#-----------------------------------



def main():
    options, args = cmdparameter(sys.argv)
    #-----------------------------------
    file = options.filein
    sampleGroup = options.sampleGroup
    verbose = options.verbose
    global debug
    debug = options.debug
    if sampleGroup:
        sampleGroupD = sampleGroupDetermine(file, sampleGroup)
    else:
        sampleGroupD = {}
    rowSort,clusterInnerSort = determineClusterSort(file, sampleGroupD)

    if debug:
        print >>sys.stderr, rowSort
        print >>sys.stderr, clusterInnerSort

    #------------------------------------------------------
    if file == '-':
        fh = sys.stdin
    else:
        fh = open(file)
    #colSort = [int(i) for i in sys.argv[2].split('-')]
    #rowSort = [int(i) for i in sys.argv[3].split('-')]
    #if len(sys.argv) > 4:
    #    clusterInnerSort=[i.split('.') for i in sys.argv[4].split('-')]
    #else:
    #    clusterInnerSort=''
    #---------------------------
    #print >>sys.stderr, clusterInnerSort
    head = 1
    allLinesD = {}
    keySet = set()
    for line in fh:
        if head:
            headerL = line.strip().split('\t')
            head -= 1
            continue
        lineL = line.strip().split('\t')
        key = lineL[-1]
        keySet.add(key)
        if key not in allLinesD:
            allLinesD[key] = ['\t'.join(lineL[:-1])]
        else:
            allLinesD[key].append('\t'.join(lineL[:-1]))
    #---------------------------------------------
    if len(lineL) > len(headerL):
        headerL.insert(0, "ID")
    if file != '-':
        fh.close()
    keySetL = list(keySet)
    #keySetL.remove('cluster')

    #newKeySetL = [float(i) for i in keySetL if i!= 'cluster']
    #keySetL.sort(key=lambda x:float(x))
    #print allLinesD['cluster'][0]
    print '\t'.join(headerL[:-1])
    if clusterInnerSort == '':
        for key in rowSort:
            #key = keySetL[i-1]
            tmpList = allLinesD[key]
            tmpList.sort(key=lambda x:float(x.split('\t')[1]))
            print "\n".join(tmpList)
    else:
        assert len(clusterInnerSort) == len(rowSort)
        j = -1
        for key in rowSort:
            j += 1
            #key = keySetL[i-1]
            tmpList = allLinesD[key]
            tmpList.sort(key=lambda x: sortFunc(x,
                clusterInnerSort[j]))
            #j = j - 1
            print "\n".join(tmpList)

#----------------------------------------------------------
if __name__ == '__main__':
    main()

#        print >>sys.stderr, "Parse the output of heatmapS.sh to \
#reorganize the data. The first column in the head line of file \
#is unneeded. That is to say the number of columns of head line is \
#1 less than that of data line."
#        print >>sys.stderr, "Print the result to screen"
#        print >>sys.stderr, 'Using python %s filename(cluster.final)[-] \
#colSort[3-2-1 means third column be the first in new file, first be \
#the third(1-based, only data colum, exclude the first name column. \
#Default data value will be sorted by new first data column.)] \
#rowSort[4-2-3-5-1 means forth cluster rows be the first 1,from \
#down-top] \
#clusterSort[Default each cluster is sorted by values in first \
#sample in new file. Accept 1-2-3 means first cluster(here cluster 1) \
#sort by first \
#sample, second cluster sort by second sample. Or 1-2.3-4 means second \
#custer sort by the sum of sample2 and sample3. Here the sort of this \
#parameter should be accordant with rowSort. Elements separated by dash \
#should be the same number of cluster. Actually they are \
#negative correlation,  the program will treat with it.' % sys.argv[0]
#        sys.exit(0)
#
#
