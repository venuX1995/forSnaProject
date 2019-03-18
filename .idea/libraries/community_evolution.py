#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : community_evolution.py
# @Author: xuan
# @Date  : 2019-03-08
# @Desc  : All about evolution of community
import csv
import pandas as pd
from pandas import DataFrame,Series
import numpy as np
import matplotlib
import networkx as nx
import community
import community.community_status


def transformDict(dict):      #将社区探测函数返回的节点-社区字典转换为社区-节点集字典
    newDict = {}
    for key,val in dict.items():
        newDict.setdefault(val,[]).append(key)
    return newDict

#def getAvgLeadership(Node):
def getLeadershipOftime(G):
    comDict = transformDict(community.best_partition(G))
    leadershipOfT = pd.DataFrame({'node':[],'community':[],'leadership_in_community':[]})
    dictOfDegree = {}
    for com in comDict:
        degreeOfAll = 0
        for node in comDict[com]:
            dictOfDegree.setdefault(node,getDegreeInCommunity(node,G,comDict[com]))
            degreeOfAll += dictOfDegree[node]
        print('社区',com,'中所有节点度的和为：',degreeOfAll)
        for node in comDict[com]:
            degree = dictOfDegree[node]
            degreeOfNeigh = degreeOfAll - degree
            edgeOfNeigh = (degreeOfAll - degree*2)/2
            if(degree == 0):
                cfc = 0.01
            elif(degree == 1):
                cfc = 1
            else:
                cfc = 2*edgeOfNeigh/(degree*(degree-1))
            leadership = round(degree/(cfc+degreeOfNeigh),3)
            print('社区',com,'中节点',node,'的度为：',degree,' ','它的邻居节点总度数为',degreeOfNeigh,'它的领导力为：',leadership)
            leadershipOfT = leadershipOfT.append((DataFrame({'node':[node],'community':[com],'leadership_in_community':[leadership]})))
    leadershipOfT.set_index(['node'],inplace=True)
    return leadershipOfT

def getIndexInCommunity(node,com,df):
    comInfo = DataFrame(df[df['community']==com])
    rank = comInfo['leadership_in_community'].rank(ascending=False)[node]
    index = round(rank/comInfo.shape[0])
    return index


def getDegreeInCommunity(node,G,comList):
    degree = 0
    neigh_list = nx.all_neighbors(G,node)
    return len(list((set(comList).union(set(neigh_list))) ^ (set(comList) ^ set(neigh_list))))



def computeStability(dic1,dic2):    #计算两个社区的稳定性
    matrixOfStability = DataFrame({'community_of_T1':[],'community_of_T2':[],'stability':[]})
    for c1 in dic1:
        for c2 in dic2:
            a_list = dic1[c1]
            b_list = dic2[c2]
            intersectionList = list((set(a_list).union(set(b_list))) ^ (set(a_list) ^ set(b_list)))
            sameNodeCount = len(intersectionList)
            sta = max(sameNodeCount / len(a_list), sameNodeCount / len(b_list))
            matrixOfStability.append(DataFrame({'c1':c1,'c2':c2,'sta':sta}),ignore_index=True)
    return matrixOfStability


def computeDifference(G1,G2):    #计算模块差异度
    diff = DataFrame ({'community_of_T1':[],'community_of_T2':[],'difference':[]})
    leadershipOfG1 = getLeadershipOftime(G1)
    leadershipOfG2 = getLeadershipOftime(G2)
    dic1 = transformDict(community.best_partition(G1))
    dic2 = transformDict(community.best_partition(G2))
    for c1 in dic1:
        for c2 in dic2:
            a_list = dic1[c1]
            b_list = dic2[c2]
            intersectionList = list((set(a_list).union(set(b_list))) ^ (set(a_list) ^ set(b_list)))
            difference = 0
            for Node in intersectionList:
                index1 = getIndexInCommunity(Node,c1,leadershipOfG1);     #节点在c1中的影响力排名
                index2 = getIndexInCommunity(Node,c2,leadershipOfG2);     #节点在c2中的影响力排名
                leadership = (leadershipOfG1.get_value(Node,leadership_in_community)+leadershipOfG2.get_value(Node,leadership_in_community))/2    #需要重写
                difference = difference + abs(index1-index2)*leadership
            difference = difference/len(intersectionList)
            diff.append(DataFrame({'c1': c1, 'c2': c2, 'difference': round(difference,3)}), ignore_index=True)
    return diff

def getSimilarity(alpha,beta,sta,diff):
    if(diff <= alpha & sta >= beta):
        return 1
    return 0

def norm(data):         #数据归一化
    min = data.min(0)
    max = data.max(0)
    data_shape = data.shape
    data_rows = data_shape[0]
    data_cols = data_shape[1]
    normData = np.empty((data_rows,data_cols))
    for i in xrange(data_cols):
        normData[:,i] = (data[:,i] - min[i])/(max[i] - min[i])
    return normData

# def evolutionClassifier(alpha,beta,partition1,partition2):  #alpha和beta是人为设定的参数,p1,p2是两个时间窗口的社区划分字典
#
#     if (sim == 0):
#         return 0  # 参数0代表两个社区没有演化关系
#     length1 = len(c1)
#     length2 = len(c2)
#     intersection = len(list((set(c1).union(set(c2))) ^ (set(c1) ^ set(c2))))
#     sameRatio = intersection/length1
#     if(sameRatio >= 0.9):
#         return 1           #延续continuing
#     elif(length2 > length1 & (length2-length1)/length1 >=0.1):
#         return 2           #生长growing
#     elif(length2 < length1 & (length1-length2)/length1 >=0.1):
#         return 3           #萎缩shrinking
