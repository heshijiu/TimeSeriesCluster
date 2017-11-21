#!/usr/bin/Python
# -*- coding: utf-8 -*-
##Utils Functions for processing single including time series single
import pywt
from dtw import dtw
import numpy as np
import math

spuTol = 1e-9
###Normal a single####
def Normal(x):
    if len(x) == 0:
        return 0
    total = 0
    for item in x:
        total += item*item
    total = total ** 0.5
    if total != 0:
        for i in range(0, len(x)):
            x[i] /= total
    return
#############
###Parameter Single###
def Parameter(single, up, down):
    count = len(single)
    max = single[count -1]
    min = single[0]
    newsingle = []
    for i in range(0, count):
        if single[i] > max:
            max = single[i]
        elif single[i] < min:
            min = single[i]
    if (abs(max-min) < 1e-9) or (abs(max) < 1e-9) or (abs(min) < 1e-9):
        return None
    for i in range(0,count):
        item = down + (single[i] - min)/(max - min)*(up - down)
        newsingle.append(item)
    return newsingle
######################################
###Wavelet Simplify###
def WaveletSimplify(single = None, level = None, levelType = 'auto', maxMinsize = None, ifNorm = True):
    if single == None:
        return
    singleSize = len(single)
    if level == None and levelType == 'auto':
        w = pywt.Wavelet('db1')
        maxLevel = pywt.dwt_max_level(singleSize, w.dec_len)
        level = int(maxLevel / 2) + 1
    if level == None and levelType == 'singleSize' and maxMinsize != None:
        if abs(maxMinsize) < spuTol:
            print("Wrong simplify size")
            return None
        doubleLevel = math.log(float(singleSize)/float(maxMinsize), 2)
        intLevel = int(doubleLevel)
        if abs(intLevel - doubleLevel) < 0.5:
            level = intLevel
        else:
            level = intLevel + 1
    cA = pywt.wavedec(single, 'db1', level=level)
    newsingle = []
    for i in range(0,len(cA[0])):
        newsingle.append(cA[0][i])
    Normal(newsingle)
    if ifNorm:
        return newsingle
    else:
        return cA[0]
########################################################
###Get DTW of two singles
def GetDTWOfTwoSingles(single1 = None, single2 = None):
    if single1 == None or single2 == None:
        return None
    x = np.array(single1).reshape(-1, 1)
    y = np.array(single2).reshape(-1, 1)
    try:
        dist, cost, acc, path = dtw(x, y, dist=lambda x, y: np.linalg.norm(x - y, ord=1))
    except:
        return None
    else:
        return dist
    return

if __name__ == "__main__":
    print("SingleProcessUtils")