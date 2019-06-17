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
    match_id_target = Series(match_id_target.match_id.unique()).sort_values()
    print(match_id_target)
    graph_list = []
    community_list = []
    evoDict_list = []
    alpha = 0.3
    beta = 0.2
    gNow = nx.Graph()
    #循环建立各个比赛的网络,并划分社区
    for index,mid in match_id_target.iteritems():
        G = aboutGraph.window_based_on_activity(data,mid)
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
    return evoDict_list

evoDict_list_4_reward_match = network_on_activity(f,[1,2])
evoDict_list_4_non_reward_match = network_on_activity(f,[3])