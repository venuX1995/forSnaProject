#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : executor.py
# @Author: xuan
# @Date  : 2019-03-19
# @Desc  : 使用其他.py中的工具运行主函数。主函数包括得到分时图，各个图的节点数量（一组数字），社区数目（一组数字），
import aboutGraph
import networkx as nx
import sys
import matplotlib.pyplot as plt
import numpy as np
import csv
import community
import pandas as pd
from pandas import Series,DataFrame
import tools
import community_evolution
import json

#将字典写入文件的方法
# with open(p+'dictionary/'+'staDict'+str(count)+'.csv','w+') as f_out1:
            #     for key,val in staDict.items():
            #         f_out1.write(key+"\t"+json.dumps(val,ensure_ascii=False))
            #         print("将字典写入文件……")
            #         f_out1.write("\n")

p = '/users/xuan/desktop/SNA/data/'
f = p+'edges_with_timestamps20190508.csv'
rewardMatch = p+'match_table用于甘特图标记.csv'
matchInfo = pd.read_csv(rewardMatch)

count = 1 #时间切片计数器
T: int = 5172240*2 #四个月的时间窗
start = 1431705600
endTimeStamp = 1557676799
end = start+T
alpha = 0.3
beta = 0.2
gCur = nx.Graph()  #所有的演化计算需要在相邻的两个时间切片上进行，两个g分别代表当前时间切片及下一个时间切片
gPre = nx.Graph()
gNext = nx.Graph()
comDictNow,comDictPre,comDictNext = {},{},{}
diffDictPre,diffDictNext = {},{}
evoDictSum = {}
staDictNext: dict
staDictPre,staDictNext = {},{}
dataForVisual = DataFrame({'时间切片':[],'事件':[],'数量':[],'演化事件所占的百分比':[],'日期':[]})
leadership = pd.DataFrame({'nodeID':[],'community':[],'leadership_in_community':[]})
sizeOfNetwork = DataFrame({'时间切片':[],'人数':[],'累积人数':[],'线上比赛':[],'线下比赛':[]})
cumulativeSize = set()
while end<endTimeStamp:        #循环建立每个静态网络 并输出每两个图之间的稳定性字典和差异性字典
    G = aboutGraph.generate(f,start,end)
    cumulativeSize.update(nx.nodes(G))
    onlineReward, offlineReward = 0, 0
    for index,row in matchInfo.iterrows():
        matchStart = row['start_time']
        matchEnd = row['close_time']
        if row['线上/下']==0: #线上比赛
            if (start>=matchStart and start<=matchEnd) or(end>=matchStart and end<=matchEnd):
                onlineReward = 50
        else:
            if row['开始日期'] == row['结束日期']:  #当日结束线下比赛
                if matchStart>=start and matchStart<=end:
                    offlineReward = 60
            else:   #持续性比赛
                if (start>=matchStart and start<=matchEnd) or(end>=matchStart and end<=matchEnd):
                    offlineReward = 60
    sizeOfNetwork = sizeOfNetwork.append(DataFrame({'时间切片':[count],'人数':[nx.number_of_nodes(G)],'累积人数':[len(cumulativeSize)],'线上比赛':[onlineReward],'线下比赛':[offlineReward]}),ignore_index=True)
    comDictForLeadership = community_evolution.transformDict(community.best_partition(G))
    leadershipOfT = community_evolution.getLeadershipOftime(comDictForLeadership,G)
    leadership = leadership.append(leadershipOfT,ignore_index=True)
    if count == 1:
        gCur = G
    elif count == 2:
        gNext = G
    else:
        gPre = gCur
        gCur = gNext
        gNext = G
    if(count >=2):     #计算每个相邻时间切片之间所有社区的稳定性与差异性
        print("当前所在时间切片为第", count - 1, "个")
        comDictPre = comDictNow
        comDictNow = community_evolution.transformDict(community.best_partition(gCur))
        comDictNext: dict = community_evolution.transformDict(community.best_partition(gNext))
        if comDictPre is not None:
            staDictPre = community_evolution.computeStability(comDictPre,comDictNow,count)
            diffDictPre = community_evolution.computeDifference(gPre,gCur,comDictPre,comDictNow,count)
        if comDictNext is not None:
            staDictNext = community_evolution.computeStability(comDictNow,comDictNext,count+1)
            diffDictNext = community_evolution.computeDifference(gCur,gNext,comDictNow,comDictNext,count+1)
        evoDict = community_evolution.evolutionClassifier(alpha,beta,diffDictPre,staDictPre,diffDictNext,staDictNext,comDictNow,comDictPre,comDictNext,count)
        evoDictSum[count-1] = evoDict
        formingCount,mergingCount,growingCount,shrinkingCount,disolvingCount,splittingCount,continuingCount,sum= 0,0,0,0,0,0,0,0
        for key,val in evoDict.items():
            for event in val:
                if 'forming' in event:
                    formingCount+=1
                elif 'merging' in event:  #需要在关键字中提取merging
                    mergingCount+=1
                elif 'growing' in event:
                    growingCount+=1
                elif 'shrinking' in event:
                    shrinkingCount+=1
                elif 'disolving' in event:
                    disolvingCount+=1
                elif 'splitting' in event:
                    splittingCount+=1
                elif 'continuing' in event:
                    continuingCount+=1
        #print(formingCount,' ',mergingCount)
        print(count)
        sum = formingCount+mergingCount+growingCount+shrinkingCount+disolvingCount+splittingCount+continuingCount
        date = tools.timeTrans(start,"%Y-%m-%d")
        dataForVisual=dataForVisual.append(DataFrame({'时间切片':[count-1],'事件':['forming'],'数量':[formingCount],'演化事件所占的百分比':[formingCount/sum],'日期':[date]}),ignore_index=True)
        dataForVisual=dataForVisual.append(DataFrame({'时间切片': [count-1], '事件': ['merging'], '数量': [mergingCount],'演化事件所占的百分比':[mergingCount/sum],'日期':[date]}), ignore_index=True)
        dataForVisual=dataForVisual.append(DataFrame({'时间切片': [count-1], '事件': ['growing'], '数量': [growingCount],'演化事件所占的百分比':[growingCount/sum],'日期':[date]}), ignore_index=True)
        dataForVisual=dataForVisual.append(DataFrame({'时间切片': [count-1], '事件': ['shrinking'], '数量': [shrinkingCount],'演化事件所占的百分比':[shrinkingCount/sum],'日期':[date]}), ignore_index=True)
        dataForVisual=dataForVisual.append(DataFrame({'时间切片': [count-1], '事件': ['disolving'], '数量': [disolvingCount],'演化事件所占的百分比':[disolvingCount/sum],'日期':[date]}), ignore_index=True)
        dataForVisual=dataForVisual.append(DataFrame({'时间切片': [count-1], '事件': ['splitting'], '数量': [splittingCount],'演化事件所占的百分比':[splittingCount/sum],'日期':[date]}), ignore_index=True)
        dataForVisual=dataForVisual.append(DataFrame({'时间切片': [count-1], '事件': ['continuing'], '数量': [continuingCount],'演化事件所占的百分比':[continuingCount/sum],'日期':[date]}), ignore_index=True)
        #print(dataForVisual)
    start += T
    if (end+T)<endTimeStamp:
        end +=T
    else:
        end = endTimeStamp
    count = count+1
print(evoDictSum)
evoChain = community_evolution.computeEvolutionLength(evoDictSum)
print(evoChain)
EvolutionChain = DataFrame({'start':[],'end':[],'length':[]})
for val in evoChain:
    EvolutionChain = EvolutionChain.append(DataFrame({'start':[val[0]],'end':[val[len(val)-2]],'length':[len(val)-1]}))
EvolutionChain.to_csv(p+'evolution_chain.csv')
dataForVisual.to_csv(p+'data_to_visualization.csv')
leadershipToGroup = leadership['leadership_in_community'].groupby(leadership['nodeID'])
#print(leadershipToGroup)
leadershipToGroup.mean().to_csv(p+'avgLeadership.csv')
sizeOfNetwork.to_csv(p+'sizeOfNetwork.csv')
#leadership.to_csv(p+'leadershipOfAll.csv')