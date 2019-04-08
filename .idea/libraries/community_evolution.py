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
def getLeadershipOftime(comDict,G):
    #comDict = transformDict(community.best_partition(G))
    leadershipOfT = pd.DataFrame({'nodeID':[],'community':[],'leadership_in_community':[]})
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
            print('社区',com,'中节点',node,'的度为：',degree,' ','它的邻居节点总度数为',degreeOfNeigh,'的领导力为：',leadership)
            leadershipOfT = leadershipOfT.append((DataFrame({'nodeID':[node],'community':[com],'leadership_in_community':[leadership]})))
    #leadershipOfT.set_index(['node'],inplace=True)
    #print(leadershipOfT)
    return leadershipOfT

def getIndexInCommunity(node,com,df):
    #df.set_index(['nodeID'], inplace=True)
    #print(df)
    #print("利用社区编号和影响力值进行排序后：")
    df = df.sort_values(axis=0,by=['community','leadership_in_community'],ascending=False)
    print(df)
    comInfo = DataFrame(df[df['community']==com])
    print(comInfo)
    comInfo.set_index(['nodeID'],inplace=True)
    #print(comInfo)
    comInfo = Series(comInfo['leadership_in_community'].rank(ascending=False))
    print(comInfo)
    print("当前进行的节点为：",node)
    rank = comInfo[node]
    print(rank)
    #print(comInfo['leadership_in_community'].rank(ascending=False)[node])
    #print(comInfo['leadership_in_community'].rank(ascending=False))
    #rank = comInfo['leadership_in_community'].rank(ascending=False)[node]
    #print("节点",node,"的排序为",rank)
    index = round(rank/comInfo.shape[0],3)
    return index


def getDegreeInCommunity(node,G,comList):
    degree = 0
    neigh_list = nx.all_neighbors(G,node)
    return len(list((set(comList).union(set(neigh_list))) ^ (set(comList) ^ set(neigh_list))))



def computeStability(dic1,dic2,count):    #计算两个社区的稳定性  结果输出由两个社区确定的稳定性字典
    #dic1 = transformDict(community.best_partition(G1))
    #dic2 = transformDict(community.best_partition(G2))
    #stability = DataFrame({'community_of_T1':[],'community_of_T2':[],'stability':[]})
    stabilityDict = {}
    for c1 in dic1:
        for c2 in dic2:
            a_list = dic1[c1]
            b_list = dic2[c2]
            intersectionList = list((set(a_list).union(set(b_list))) ^ (set(a_list) ^ set(b_list)))
            sameNodeCount = len(intersectionList)
            #sta = max(sameNodeCount / len(a_list), sameNodeCount / len(b_list))
            sta = [sameNodeCount/len(a_list),sameNodeCount/len(b_list)]
            key1 = 'c'+str(count-1)+str(c1)
            key2 = 'c'+str(count)+str(c2)
            if key1 not in stabilityDict.keys():
                stabilityDict[key1] = {key2:sta} #存为嵌套字典，第一个键为t中的社区编号，第二层键为t+1中的社区编号，sta为两个社区之间的稳定性，count暂定，用来标记第几张图
            else:
                stabilityDict[key1][key2] = sta
            #stability.append(DataFrame({'c1':c1,'c2':c2,'sta':sta}),ignore_index=True)
    return stabilityDict


def computeDifference(G1,G2,dic1,dic2,count):    #计算模块差异度,dic是社区划分字典
    #diff = DataFrame ({'community_of_T1':[],'community_of_T2':[],'difference':[]})
    diffDict = {}
    #dic1 = transformDict(community.best_partition(G1))
    #dic2 = transformDict(community.best_partition(G2))
    leadershipOfG1 = getLeadershipOftime(dic1,G1)
    leadershipOfG2 = getLeadershipOftime(dic2,G2)
    for c1 in dic1:
        for c2 in dic2:
            a_list = dic1[c1]
            b_list = dic2[c2]
            print("c1中的节点包括",a_list)
            print("c2中的节点包括",b_list)
            intersectionList = list((set(a_list).union(set(b_list))) ^ (set(a_list) ^ set(b_list)))
            print("交集为：",intersectionList)
            difference = 0
            for Node in intersectionList:
                print("当前比较对象为： ","图1中的社区",c1,"和图2中的社区",c2,"中节点",Node)
                index1 = getIndexInCommunity(Node,c1,leadershipOfG1);     #节点在c1中的影响力排名
                print("节点",Node,"在c1中的排名百分比为",index1)
                index2 = getIndexInCommunity(Node,c2,leadershipOfG2);     #节点在c2中的影响力排名
                print("节点", Node, "在c2中的排名百分比为", index2)
                #leadership = (leadershipOfG1.get_value(Node,leadership_in_community)+leadershipOfG2.get_value(Node,leadership_in_community))/2    #需要重写
                leadership = ((leadershipOfG1['leadership_in_community'][leadershipOfG1['nodeID']==Node].values[0])+(leadershipOfG2['leadership_in_community'][leadershipOfG2['nodeID']==Node].values[0]))/2
                difference = difference + abs(index1-index2)*leadership
            difference = difference/(len(intersectionList)+0.001)
            key1 = 'c' + str(count - 1) + str(c1)
            key2 = 'c' + str(count) + str(c2)
            if key1 not in diffDict.keys():
                diffDict[key1] = {key2:difference} #存为嵌套字典，第一个键为t中的社区编号，第二层键为t+1中的社区编号，difference为两个社区之间的差异性，count暂定，用来标记第几张图
            else:
                diffDict[key1][key2] = difference
            #diff.append(DataFrame({'c1': c1, 'c2': c2, 'difference': round(difference,3)}), ignore_index=True)
    return diffDict

def getSimilarity(alpha,beta,staDict,diffDict,c1,c2):    #alpha和beta为两个人为设定的参数，staDict和diffDict为稳定和差异字典，c1为t中的社区，c2为t+1中的社区
    sta = staDict[c1][c2]
    diff = diffDict[c1][c2]
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


#社区演化分类器，alpha，beta为设定的参数，Pre为与上一张图比较得到的字典，Next是与下一张图比较得到的字典,comDict为当前需要进行判断的图的社区字典（中间图）
# 需要和上一个图进行对比的状态：forming、merging
# 需要和下一个图进行对比的状态：continuing、growing、shrinking、spliting、disolving
# forming：与上一张图中的每一个社区对比是否存在演化关系（01二值）；
# continuing：下一张图里只存在一个社区与其sim为1，并且结构相似占比（占自己）的比重超过90 %；
# growing：下一张图里只存在一个社区满足sim = 1，且大于自己的规模超过10 %；
# shrinking：下一张图里只存在一个社区满足sim = 1，且小于自己的规模超过10 %；
# splitting：下一张图里存在多个社区满足，这些社区规模都比该社区小，且差异性 <= alpha + 0.1, 稳定性 > beta
# Merging：上一张图里存在多个社区满足，规模小于该社区，且差异性 <= alpha + 0.1, 稳定性 > beta
# dissolving：下一张图里不存在任何社区满足sim = 1

def evolutionClassifier(alpha,beta,diffDictPre,staDictPre,diffDictNext,staDictNext,comDictNow,comDictPre,comDictNext):
    evolutionDict = {}    #计划将状态存为字典，共有7种状态，每一个key对应的val为一个长度为2的list，list[0]为与上一张图的关系，list[1]为与下一张图的关系
    if not comDictPre is None:   #先判断和上一张图的对比，得出对于Forming和merging的判断，G1不进入此段代码块，其中社区默认全部为forming
        for keyNow in comDictNow:
            simCountPre = 0;
            for keyPre in diffDictPre:
                if getSimilarity(alpha,beta,staDictPre,diffDictPre,keyPre,keyNow)!=0:
                    simCountPre += 1
            if simCountPre == 0:
                evolutionDict[keyNow] = ['forming']
            if simCountPre > 1:
                evolutionDict[keyNow] = ['merging']
    elif comDictPre is None:
        for keyNow in comDictNow:
            evolutionDict[keyNow] = ['forming']
    #与下一张图的对比
    if not comDictNext is None:  #和下一张图的对比，得到剩余五个状态的判别
        for keyNow in comDictNow:
            simCountNext = 0
            simDictList = []
            for keyNext in diffDictNext:
                if getSimilarity(alpha,beta,staDictNext,diffDictNext,keyNow,keyNext)!=0:
                    simDictList.append(keyNext)
                    simCountNext += 1
            if simCountNext == 0:
                evolutionDict[keyNow].append('disolving')
            elif simCountNext == 1:
                ratio = len(comDictNext[keyNext])/len(comDictNow[keyNow])
                if(ratio>1.1):
                    evolutionDict[keyNow].append('growing')
                elif(ratio<0.9):
                    evolutionDict[keyNow].append('shrinking')
                elif(ratio>=0.9 & ratio<=1.1):
                    evolutionDict[keyNow].append('continuing')
            else:
                evolutionDict[keyNow].append('splitting')
    print("当前图的演化字典为：")
    print(evolutionDict)



