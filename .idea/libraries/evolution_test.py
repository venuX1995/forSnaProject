#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : evolution_test.py
# @Author: xuan
# @Date  : 2019-03-22
# @Desc  : a test using two small networks for evolution
import csv
import pandas as pd
from pandas import DataFrame,Series
import numpy as np
import matplotlib
import networkx as nx
import community

def computeStabilityAndDifference(dic1,dic2):    #计算两个社区的稳定性及差异性
    matrixOfStability = DataFrame({'community_of_T1':[],'community_of_T2':[],'stability':[]})
    matrixOfDifference = DataFrame({'community_of_T1': [], 'community_of_T2': [], 'difference': []})
    for c1 in dic1:
        for c2 in dic2:
            a_list = dic1[c1]
            b_list = dic2[c2]
            intersectionList = list((set(a_list).union(set(b_list))) ^ (set(a_list) ^ set(b_list)))
            sameNodeCount = len(intersectionList)
            sta = max(sameNodeCount / len(a_list), sameNodeCount / len(b_list))
            diff = max(len(a_list)/len(b_list),len(b_list)/len(a_list))
            matrixOfStability.append(DataFrame({'c1':c1,'c2':c2,'sta':sta}),ignore_index=True)
            matrixOfDifference.append(DataFrame({'c1':c1,'c2':c2,'diff':diff}),ignore_index=True)
    return matrixOfStability,matrixOfDifference

# def generateEvolutionMatrix(dic1,dic2):
#     matrixOfStability,matrixOfDifference = computeStabilityAndDifference(dic1,dic2)
#     evolutionMatrix = np.zeros((len(dic1.keys()),len(dic2.keys())))    #初始化进化矩阵，row为T1，column为T2
#     for c1 in dic1:
#         for c2 in dic2:
#             if matrixOfStability.at[c1,c2]>=0.5 and matrixOfDifference.at[c1,c2]<=50:
#                 evolutionMatrix[]