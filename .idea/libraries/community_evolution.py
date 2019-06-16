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
    leadershipOfT = pd.DataFrame({'nodeID':[],'community':[],'leadership_in_community':[]})
    dictOfDegree = {}
    for com in comDict:
        degreeOfAll = 0
        for node in comDict[com]:
            dictOfDegree.setdefault(node,getDegreeInCommunity(node,G,comDict[com]))
            degreeOfAll += dictOfDegree[node]
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
            leadershipOfT = leadershipOfT.append((DataFrame({'nodeID':[node],'community':[com],'leadership_in_community':[leadership]})))
    return leadershipOfT

def getIndexInCommunity(node,com,df):
    df = df.sort_values(axis=0,by=['community','leadership_in_community'],ascending=False)
    comInfo = DataFrame(df[df['community']==com])
    comInfo.set_index(['nodeID'],inplace=True)
    comInfo = Series(comInfo['leadership_in_community'].rank(ascending=False))
    rank = comInfo[node]
    index = round(rank/comInfo.shape[0],3)
    return index


def getDegreeInCommunity(node,G,comList):
    degree = 0
    neigh_list = nx.all_neighbors(G,node)
    return len(list((set(comList).union(set(neigh_list))) ^ (set(comList) ^ set(neigh_list))))

def computeStability(dic1,dic2,count):    #计算两个社区的稳定性  结果输出由两个社区确定的稳定性字典
    stabilityDict = {}
    for c1 in dic1:
        for c2 in dic2:
            a_list = dic1[c1]
            b_list = dic2[c2]
            intersectionList = list((set(a_list).union(set(b_list))) ^ (set(a_list) ^ set(b_list)))
            sameNodeCount = len(intersectionList)
            sta = [sameNodeCount/len(a_list),sameNodeCount/len(b_list)]
            key1 = 'c'+str(count-2)+str(c1)
            key2 = 'c'+str(count-1)+str(c2)
            if key1 not in stabilityDict.keys():
                stabilityDict[key1] = {key2:sta} #存为嵌套字典，第一个键为t中的社区编号，第二层键为t+1中的社区编号，sta为两个社区之间的稳定性，count暂定，用来标记第几张图
            else:
                stabilityDict[key1][key2] = sta
    return stabilityDict


def computeDifference(G1,G2,dic1,dic2,count):    #计算模块差异度,dic是社区划分字典
    diffDict = {}
    leadershipOfG1 = getLeadershipOftime(dic1,G1)
    leadershipOfG2 = getLeadershipOftime(dic2,G2)
    for c1 in dic1:
        for c2 in dic2:
            a_list = dic1[c1]
            b_list = dic2[c2]
            intersectionList = list((set(a_list).union(set(b_list))) ^ (set(a_list) ^ set(b_list)))
            difference = 0
            for Node in intersectionList:
                index1 = getIndexInCommunity(Node,c1,leadershipOfG1);     #节点在c1中的影响力排名
                index2 = getIndexInCommunity(Node,c2,leadershipOfG2);     #节点在c2中的影响力排名
                #leadership = (leadershipOfG1.get_value(Node,leadership_in_community)+leadershipOfG2.get_value(Node,leadership_in_community))/2    #需要重写
                leadership = ((leadershipOfG1['leadership_in_community'][leadershipOfG1['nodeID']==Node].values[0])+(leadershipOfG2['leadership_in_community'][leadershipOfG2['nodeID']==Node].values[0]))/2
                difference = difference + abs(index1-index2)*leadership
            difference = difference/(len(intersectionList)+0.001)
            key1 = 'c' + str(count - 2) + str(c1)
            key2 = 'c' + str(count - 1) + str(c2)
            if key1 not in diffDict.keys():
                diffDict[key1] = {key2:difference} #存为嵌套字典，第一个键为t中的社区编号，第二层键为t+1中的社区编号，difference为两个社区之间的差异性，count暂定，用来标记第几张图
            else:
                diffDict[key1][key2] = difference
    return diffDict

def getSimilarity(alpha,beta,staDict,diffDict,c1,c2):    #alpha和beta为两个人为设定的参数，staDict和diffDict为稳定和差异字典，c1为t中的社区，c2为t+1中的社区
    sta = max(staDict[c1][c2][0],staDict[c1][c2][1])
    diff = diffDict[c1][c2]
    if(diff <= alpha and sta >= beta):
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

def evolutionClassifier(alpha,beta,diffDictPre,staDictPre,diffDictNext,staDictNext,comDictNow,comDictPre,comDictNext,count):
    evolutionDict = {}    #计划将状态存为字典，共有7种状态，每一个key对应的val为一个长度为2的list，list[0]为与上一张图的关系，list[1]为与下一张图的关系
    #和上一张图的对比
    if not comDictPre is None:   #先判断和上一张图的对比，得出对于Forming和merging的判断，G1不进入此段代码块，其中社区默认全部为forming
        for keyNow in comDictNow:
            key1Now = 'c' + str(count - 1) + str(keyNow)
            simDictListWithPre = []
            simCountPre = 0;
            for keyPre in comDictPre:
                key2Pre = 'c' + str(count-2) + str(keyPre)
                if getSimilarity(alpha,beta,staDictPre,diffDictPre,key2Pre,key1Now)!=0:
                    simDictListWithPre.append(key2Pre)
                    simCountPre += 1
            if simCountPre == 0:
                evolutionDict[key1Now] = ['forming']
            if simCountPre == 1:
                evolutionDict[key1Now] = ['comingFrom '+simDictListWithPre[0]]
            if simCountPre > 1:
                #evolutionDict[key1Now] = ['merging']
                evolutionDict[key1Now] = ['mergingFrom '+','.join(simDictListWithPre)]
    elif comDictPre is None:
        for keyNow in comDictNow:
            evolutionDict[keyNow] = ['forming']
    #与下一张图的对比
    if not comDictNext is None:  #和下一张图的对比，得到剩余五个状态的判别
        for keyNow in comDictNow:
            key1 = 'c' + str(count - 1) + str(keyNow)
            simCountNext = 0
            simDictListWithNext = []
            for keyNext in comDictNext:
                key2 = 'c' + str(count) + str(keyNext)
                if getSimilarity(alpha,beta,staDictNext,diffDictNext,key1,key2)!=0:
                    simDictListWithNext.append(key2)
                    simCountNext += 1
            if simCountNext == 0:
                evolutionDict[key1].append('disolving')
            elif simCountNext == 1:
                keyNextTemp = int(simDictListWithNext[0][len(str(count-1))+1:len(simDictListWithNext[0])])
                ratio = len(comDictNext[keyNextTemp])/len(comDictNow[keyNow])   #TODO
                if(ratio>1.1):
                    evolutionDict[key1].append('growingTo '+simDictListWithNext[0])
                elif(ratio<0.9):
                    evolutionDict[key1].append('shrinkingTo '+simDictListWithNext[0])
                elif(ratio>=0.9 and ratio<=1.1):
                    evolutionDict[key1].append('continuingTo '+simDictListWithNext[0])
            else:
                evolutionDict[key1].append('splittingTo '+','.join(simDictListWithNext))
    elif comDictNext is None:
        for keyNow in comDictNow:
            evolutionDict[key1].append('disolving')
    print("当前图的演化字典为：")
    print(evolutionDict)
    return evolutionDict

def computeEvolutionLength(evolutionDict): #输出所有演化链
    resultList = []
    for key,value in evolutionDict.items():
        for group in value:
            if value[group][0]=='forming':
                evoList = ['formingFrom '+group]
                checkChain(resultList,evoList,evolutionDict,group,key)
    return resultList

def decompose(nextState):
    nextComList = []
    tempList = nextState.split(' ')
    event = tempList[0]
    if len(tempList)==2:
        nextComList = tempList[1].split(',')
    return event,nextComList

#利用递归法得到演化链，输入用于拼接的链头、字典、查询的社区，当前所在的时间窗口
def checkChain(resultList,evolist,evodict,com,timeSlot):
    evodictOfNow = evodict[timeSlot]
    print('当前时间窗口的字典')
    print(evodictOfNow)
    print('需要查找的社区:'+com)
    nextState = evodictOfNow[com][1]
    event,nextComList = decompose(nextState) #event:String 存储演化事件
    print("演化链进入第"+str(timeSlot)+'个时隙')
    if event == 'disolving' or timeSlot==len(evodict):   #最后一个时间窗口 需要手动设置
        evolist.append('disolving')
        resultList.append(evolist)
        print("event是disolving")
        print('加入结果集')
        print(evolist)
        return
    else:
        print('event不是disolving而是'+event+' 进入递归')
        for group in nextComList:
            length = timeSlot
            if(timeSlot>1):
                while len(evolist)>timeSlot:
                    evolist.pop()
            print('递归到社区'+com+'的后继社区'+group)
            evolist.append(event+' '+group)
            checkChain(resultList,evolist,evodict,group,timeSlot+1)



