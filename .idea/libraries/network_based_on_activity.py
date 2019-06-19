#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : network_based_on_activity.py
# @Author: xuan
# @Date  : 2019-06-16
# @Desc  : 本文件中取代时间窗格的概念，以激励性的活动作为建立网络的基础。所有的处理与分析都基于活动窗格
import pandas as pd
from pandas import Series,DataFrame
import networkx as nx
import sys
import tools
import community_evolution
import quantization
import aboutGraph
import community

p = '/users/xuan/desktop/SNA/data/'
f = p+'edge_with_match_info.csv'
#match_type传入一个 list，存有需要以事件窗格作为观察基础的比赛类型
def network_on_activity(f,match_type):
    data = pd.read_csv(f)
    match_id_target = DataFrame({})
    for type in match_type:
        match_id_target = match_id_target.append(data.loc[data['match_type']==type])
    match_id_target = list(Series(match_id_target.match_id.unique()).sort_values())
    print(match_id_target)
    graph_list = []
    community_list = []
    evoDict_list = []
    alpha = 0.3
    beta = 0.2
    gNow = nx.Graph()
    #循环建立各个比赛的网络,并划分社区
    if len(match_type)>1: #激励性比赛
        for mid in match_id_target:
            match_id_list = [mid]
            G = aboutGraph.window_based_on_activity(data,match_id_list)
            gNow = G
            graph_list.append(gNow)
            community_list.append(community_evolution.transformDict(community.best_partition(gNow)))
    elif len(match_type)==1: #无激励
        window_size=8
        for i in range(0, int(448 / window_size) - 2):
            match_id_list = match_id_target[i * window_size:i * window_size + window_size - 1]
            G = aboutGraph.window_based_on_activity(data, match_id_list)
            gNow = G
            graph_list.append(gNow)
            community_list.append(community_evolution.transformDict(community.best_partition(gNow)))

    for i in range(0,len(graph_list)-1):
        diffDictPre, staDictPre = {}, {}
        diffDictNext, staDictNext = {}, {}
        comDictPre, comDictNext = {}, {}
        comDictNow = community_list[i]
        #给diffence和stability 字典赋值
        if i>0: #和上一张图的对比
            comDictPre = community_list[i - 1]
            diffDictPre = community_evolution.computeDifference(graph_list[i-1],graph_list[i],comDictPre,comDictNow,i+1)
            staDictPre = community_evolution.computeStability(comDictPre,comDictNow,i+1)
        if i<len(graph_list)-1: #和下一张的对比
            comDictNext = community_list[i+1]
            diffDictNext = community_evolution.computeDifference(graph_list[i],graph_list[i+1],comDictNow,comDictNext,i+2)
            staDictNext = community_evolution.computeStability(comDictNow,comDictNext,i+2)
        evoDict = community_evolution.evolutionClassifier(alpha,beta,diffDictPre,staDictPre,diffDictNext,staDictNext,
                                                          comDictNow,comDictPre,comDictNext,i+1)
        evoDict_list.append(evoDict)
    return evoDict_list,community_list

evoDict_list_4_reward_match,community_list  = network_on_activity(f,[1,2])
#evoDict_list_4_non_reward_match= network_on_activity(f,[3])

data_4_visual = DataFrame({'slot_based_on_actitvity':[],'event':[],'event_count':[]})

sizeOfCommunity = DataFrame({'slot':[],'community':[],'population_in_community':[]})
#可视化各个活动窗口上各类型演化事件的数量
for i in range(0,len(evoDict_list_4_reward_match)-1):
    evoDict = evoDict_list_4_reward_match[i]
    formingCount, mergingCount, growingCount, shrinkingCount, disolvingCount, splittingCount, continuingCount, comingCount = 0, 0, 0, 0, 0, 0, 0, 0
    for key, val in evoDict.items():
        for event in val:
            if 'forming' in event:
                formingCount += 1
            elif 'merging' in event:  # 需要在关键字中提取merging
                mergingCount += 1
            elif 'growing' in event:
                growingCount += 1
            elif 'shrinking' in event:
                shrinkingCount += 1
            elif 'disolving' in event:
                disolvingCount += 1
            elif 'splitting' in event:
                splittingCount += 1
            elif 'continuing' in event:
                continuingCount += 1
            elif 'coming' in event:
                comingCount += 1
    data_4_visual = data_4_visual.append(
        DataFrame({'slot_based_on_actitvity':[str(i)],'event':['forming'],'event_count':[int(formingCount)]}),
        ignore_index=True)
    data_4_visual = data_4_visual.append(
        DataFrame({'slot_based_on_actitvity': [str(i)], 'event': ['merging'], 'event_count': [int(mergingCount)]}),
        ignore_index=True)
    data_4_visual = data_4_visual.append(
        DataFrame({'slot_based_on_actitvity': [str(i)], 'event': ['growing'], 'event_count': [int(growingCount)]}),
        ignore_index=True)
    data_4_visual = data_4_visual.append(
        DataFrame({'slot_based_on_actitvity': [str(i)], 'event': ['shrinking'], 'event_count': [int(shrinkingCount)]}),
        ignore_index=True)
    data_4_visual = data_4_visual.append(
        DataFrame({'slot_based_on_actitvity': [str(i)], 'event': ['dissolving'], 'event_count': [int(disolvingCount)]}),
        ignore_index=True)
    data_4_visual = data_4_visual.append(
        DataFrame({'slot_based_on_actitvity': [str(i)], 'event': ['splitting'], 'event_count': [int(splittingCount)]}),
        ignore_index=True)
    data_4_visual = data_4_visual.append(
        DataFrame({'slot_based_on_actitvity': [str(i)], 'event': ['continuing'], 'event_count': [int(continuingCount)]}),
        ignore_index=True)
    data_4_visual = data_4_visual.append(
        DataFrame(
            {'slot_based_on_actitvity': [str(i)], 'event': ['changeSize'], 'event_count': [int(comingCount)]}),
        ignore_index=True)

data_4_visual.to_csv(p+'non_reward_data_4_visual_based_on_activity.csv')
