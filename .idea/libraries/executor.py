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
import quantization

#将字典写入文件的方法
# with open(p+'dictionary/'+'staDict'+str(count)+'.csv','w+') as f_out1:
            #     for key,val in staDict.items():
            #         f_out1.write(key+"\t"+json.dumps(val,ensure_ascii=False))
            #         print("将字典写入文件……")
            #         f_out1.write("\n")

p = '/users/xuan/desktop/SNA/data/'
#f = p+'edges_with_timestamps20190508.csv'
f = p+'edge_with_match_info.csv'
rewardMatch = p+'match_table用于甘特图标记.csv'
matchInfo = pd.read_csv(rewardMatch)

count = 1 #时间切片计数器
T: int = 5172240/4 #半个月的时间窗
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
dataForVisual = DataFrame({'slot':[],'event':[],'count':[],'event_percent':[],'date':[]})
leadership = pd.DataFrame({'nodeID':[],'community':[],'leadership_in_community':[]})
#sizeOfNetwork = DataFrame({'slot':[],'population':[],'accumulation':[],'online_match':[],'offline_match':[]})
sizeOfNetwork = DataFrame({'slot':[],'population':[],'accumulation':[],'online_match':[],'offline_match':[],'slot_type':[]})
sizeOfCommunity = DataFrame({'slot':[],'community':[],'population_in_community':[]})
#event_about_match = DataFrame({'slot': [], 'group_id': [], 'm1': [], 'm2': [], 'm3': [], 'event': []})
event_about_match = DataFrame({'slot': [], 'match_type': [], 'event': [], 'count':[]})
cumulativeSize = set()
while end<endTimeStamp:        #循环建立每个静态网络 并输出每两个图之间的稳定性字典和差异性字典
    #G = aboutGraph.generate(f,start,end)  #建立定长时间窗
    #非定长时间窗建立
    sys.setrecursionlimit(1000000)
    G,end,slot_type= aboutGraph.generateIrregularGraph(f,start,T)
    cumulativeSize.update(nx.nodes(G))
    onlineReward, offlineReward = 0, 0
    for index,row in matchInfo.iterrows():   #用于可视化线上线下比赛
        matchStart = row['start_time']
        matchEnd = row['close_time']
        if row['match_type']==2: #线上比赛
            if (start>=matchStart and start<=matchEnd) or(end>=matchStart and end<=matchEnd):
                onlineReward = 1
        else:
            if row['开始日期'] == row['结束日期']:  #当日结束线下比赛
                if matchStart>=start and matchStart<=end:
                    offlineReward = 2
            else:   #持续性比赛
                if (start>=matchStart and start<=matchEnd) or(end>=matchStart and end<=matchEnd):
                    offlineReward = 2   ##
    sizeOfNetwork = sizeOfNetwork.append(DataFrame({'slot':[count],'population':[nx.number_of_nodes(G)],'accumulation':[len(cumulativeSize)],'online_match':[onlineReward],'offline_match':[offlineReward],'slot_type':[slot_type]}),ignore_index=True)
    comDictForLeadership = community_evolution.transformDict(community.best_partition(G))
    #统计社区的size分布
    for com in comDictForLeadership:
        sizeOfCommunity = sizeOfCommunity.append(DataFrame({'slot':[count],'community':[com],'population_in_community':[len(comDictForLeadership[com])]}))
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
        evoDict = community_evolution.evolutionClassifier(alpha,beta,diffDictPre,staDictPre,diffDictNext,staDictNext,comDictNow,comDictPre,comDictNext,count)  #对应 comDictNow 的进化字典
        temp_event_with_match = quantization.event_with_match(comDictNow,evoDict,f,count,T)
        print('group的比赛构成情况')
        print(temp_event_with_match)
        event_about_match = event_about_match.append(temp_event_with_match,ignore_index=True)
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
        print(count)
        sum = formingCount+mergingCount+growingCount+shrinkingCount+disolvingCount+splittingCount+continuingCount
        date = tools.timeTrans(start,"%Y-%m-%d")
        dataForVisual=dataForVisual.append(DataFrame({'slot':[count-1],'event':['forming'],'count':[formingCount],'event_percent':[formingCount/sum],'date':[date]}),ignore_index=True)
        dataForVisual=dataForVisual.append(DataFrame({'slot': [count-1], 'event': ['merging'], 'count': [mergingCount],'event_percent':[mergingCount/sum],'date':[date]}), ignore_index=True)
        dataForVisual=dataForVisual.append(DataFrame({'slot': [count-1], 'event': ['growing'], 'count': [growingCount],'event_percent':[growingCount/sum],'date':[date]}), ignore_index=True)
        dataForVisual=dataForVisual.append(DataFrame({'slot': [count-1], 'event': ['shrinking'], 'count': [shrinkingCount],'event_percent':[shrinkingCount/sum],'date':[date]}), ignore_index=True)
        dataForVisual=dataForVisual.append(DataFrame({'slot': [count-1], 'event': ['disolving'], 'count': [disolvingCount],'event_percent':[disolvingCount/sum],'date':[date]}), ignore_index=True)
        dataForVisual=dataForVisual.append(DataFrame({'slot': [count-1], 'event': ['splitting'], 'count': [splittingCount],'event_percent':[splittingCount/sum],'date':[date]}), ignore_index=True)
        dataForVisual=dataForVisual.append(DataFrame({'slot': [count-1], 'event': ['continuing'], 'count': [continuingCount],'event_percent':[continuingCount/sum],'date':[date]}), ignore_index=True)
        #print(dataForVisual)
    #start += T
    start = end
    if (start+T) < endTimeStamp:
        end = start+T
    else:
        end = endTimeStamp
    count = count+1
# evoChain = community_evolution.computeEvolutionLength(evoDictSum)
# print(evoChain)
# EvolutionChain = DataFrame({'start':[],'end':[],'length':[]})
# for val in evoChain:
#     EvolutionChain = EvolutionChain.append(DataFrame({'start':[val[0]],'end':[val[len(val)-2]],'length':[len(val)-1]}))
# EvolutionChain.to_csv(p+'evolution_chain.csv')
dataForVisual.to_csv(p+'data_to_visualization_for_irregular.csv')
leadershipToGroup = leadership['leadership_in_community'].groupby(leadership['nodeID'])
#print(leadershipToGroup)
event_about_match.to_csv(p+'event_about_match.csv')
sizeOfCommunity.to_csv(p+'sizeOfCommunity_irregular.csv')
leadershipToGroup.mean().to_csv(p+'avgLeadership.csv')
sizeOfNetwork.to_csv(p+'sizeOfNetwork_irregular.csv')
#leadership.to_csv(p+'leadershipOfAll.csv')