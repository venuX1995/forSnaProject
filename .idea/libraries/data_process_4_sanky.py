#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : data_process_4_sanky.py
# @Author: xuan
# @Date  : 2019-06-17
# @Desc  : 桑基图的数据预处理

import pandas as pd
from pandas import DataFrame,Series
import networkx as nx
import community
import aboutGraph

p = '/users/xuan/desktop/SNA/data/'
f = p+'edge_with_match_info.csv'
match_type = [3]
data = pd.read_csv(f)
match_id_target = DataFrame({})
for type in match_type:
    match_id_target = match_id_target.append(data.loc[data['match_type']==type])
match_id_target = Series(match_id_target.match_id.unique()).sort_values()
partition_list = []
gNow = nx.Graph()
data_4_sanky = DataFrame({'source':[],'target':[],'label':[],'value':[]})  #member 是一个 list
com_index = Series([])
#得到 louvain 算法算出的所有目标比赛的社区划分partition_list，key 为用户，val 为所属的社区
for index, mid in match_id_target.iteritems():
    G = aboutGraph.window_based_on_activity(data, mid)
    gNow = G
    partition_list.append(community.best_partition(gNow))

#给所有的社区编号
for i in range(0,len(partition_list)-1):
    com_list = list(set(partition_list[i].values()))
    for com in com_list:
        com_name = str(i)+'_'+str(com)
        com_index = com_index.append(Series([com_name]))
com_index = com_index.append(Series(['消失']))
com_index = com_index.reset_index(drop=True)


for i in range(0,len(partition_list)-2):
    partition_now = partition_list[i]
    for user,com in partition_now.items():
        quit_network = True
        quit_index = com_index[com_index.values == '消失'].index[0]
        source_com = str(i) + '_' + str(com)
        source_com_index = com_index[com_index.values == source_com].index[0]
        for j in range(i+1,len(partition_list)-2):  #遍历后续的社区，找到第一个出现该用户的社区
            if user in partition_list[j].keys():   #如果在后续社区中找到了该用户
                target_com = str(j)+'_'+str(partition_list[j][user])
                target_com_index = com_index[com_index.values == target_com].index[0]
                if not data_4_sanky.loc[data_4_sanky['source']==source_com_index].loc[data_4_sanky['target']==target_com_index].empty: #如果结果集中已经存在相同的s 和 t
                    exist_index = data_4_sanky.loc[data_4_sanky['source'] == source_com_index].loc[data_4_sanky['target'] == target_com_index,'label'].index[0]
                    data_4_sanky.loc[exist_index,'label'] = data_4_sanky.loc[exist_index,'label'] +'  '+str(user)
                else:
                    data_4_sanky = data_4_sanky.append(DataFrame({'source':[source_com_index],'target':[target_com_index],'label':[str(user)]}),ignore_index=True)
                quit_network = False
                break
        if quit_network:
            if not data_4_sanky.loc[data_4_sanky['source'] == source_com_index].loc[
                data_4_sanky['target'] == quit_index].empty:  # 如果结果集中已经
                exist_index = data_4_sanky.loc[data_4_sanky['source'] == source_com_index].loc[data_4_sanky['target'] == quit_index].index[0]
                data_4_sanky.loc[exist_index,'label'] = data_4_sanky.loc[exist_index,'label'] +'  '+str(user)
            else:
                data_4_sanky = data_4_sanky.append(
                    DataFrame({'source': [source_com_index], 'target': [quit_index], 'label': [str(user)]}),ignore_index=True)

for index in data_4_sanky.index:
    value = len(data_4_sanky.loc[index,'label'].split())
    data_4_sanky.loc[index,'value']= value

com_index.to_csv(p+'community_index.csv')
data_4_sanky.to_csv(p+'data_4_sanky.csv')