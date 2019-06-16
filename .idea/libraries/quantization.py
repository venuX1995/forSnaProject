#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : quantization.py
# @Author: xuan
# @Date  : 2019-05-13
# @Desc  : 量化外部因素包括组队约束（组队上限、队伍数量、比赛的激励措施）
import csv
import numpy as np
import codecs
import csv
import pandas as pd
from pandas import DataFrame,Series
import matplotlib as plt
import community_evolution

#统计不同的激励措施在各个时间窗口上的指标值（ppl_in_team/team_limit/awards)
#最终得出的应该是以激励措施和激励措施下面的具体划分为双索引（或者加上激励措施下面的具体划分成为三索引？）的字典
def statistcsGenerator(start,end,f):#输入为时间窗起始时间、match_table
    # f_in = open(f, 'r')
    # csv_reader = csv.reader(f_in, dialect='excel')
    match_dataframe = pd.read_csv(f,low_memory=False,encoding='UTF-16')
    statisticsDict = {'person_limit':[],'team_limit':[],'reward':[]}
    #TODO：这里的窗格筛选条件写的还有问题
    match_dataframe1 = match_dataframe.loc[((match_dataframe['start_time']>=start)&(match_dataframe['start_time']<=end))]
    match_dataframe2 = match_dataframe.loc[((match_dataframe['close_time']>=start)&(match_dataframe['close_time']<=end))]
    match_dataframe3 = match_dataframe.loc[((match_dataframe['start_time']<=start)&(match_dataframe['close_time']>=end))]#根据起始时间戳将时间窗内的数据筛选出来
    print("mdf3:")
    print(match_dataframe3)
    match_dataframe = (match_dataframe1.append(match_dataframe2,ignore_index=True)).append(match_dataframe3,ignore_index=True)
    match_dataframe.drop_duplicates()
    #1.计算队内人数的限制
    statisticsDict['person_limit'] = match_dataframe.loc[match_dataframe['ppl_in_team']<50]['ppl_in_team'].value_counts() #以series的形式存储在字典中
    #2.计算队伍数量的限制
    statisticsDict['team_limit'] = match_dataframe.loc[match_dataframe['ppl_in_team']<50]['team_limit'].value_counts()
    #3.计算激励措施的情况
    statisticsDict['reward'] = match_dataframe.loc[match_dataframe['ppl_in_team']<50]['binary_award'].value_counts()
    return statisticsDict

#本函数的输入为快照1的统计字典、快照2的统计字典、需要计算量化值的类型（人数限制、队伍数限制、虚拟/实物奖励）
def quantizationGenerator(staDict1,staDict2,target):
    sum1 = staDict1[target].sum()#计算图1中该指标的总数
    sum2 = staDict2[target].sum()
    change_sum = 0
    target_type_list = list(set(staDict1[target].index).union(set(staDict2[target].index)))
    for type in target_type_list:
        ratio1,ratio2 = 0,0
        if type in staDict1[target].index:
            ratio1 = staDict1[target][type]/sum1
        if type in staDict2[target].index:
            ratio2 = staDict2[target][type]/sum2
        change_sum += abs(ratio1-ratio2)
    return change_sum

#在整个时间序列上画出曲线图，以时间窗口的序列为横坐标
#计算与具体演化事件的关系可以将数据导出使用tableau出相关图
def quantizationInTimeline(start,end,T,f,target): #输入start,end是整个表的时间戳的第一个和最后一个，T是窗口的大小，f为match_table
    start_flag = start
    end_flag = start_flag+T
    staDict1,staDict2 = {},{}
    count = 1
    change_list = []
    while end_flag<end:
        print("当前计数为：",count)
        if count==1:
            print("进入条件一")
            staDict1 = statistcsGenerator(start_flag,end_flag,f)
        elif count==2:
            print("进入条件二")
            staDict2 = statistcsGenerator(start_flag,end_flag,f)
            change_list.append(quantizationGenerator(staDict1,staDict2,target))
        else:
            print("进入条件三")
            staDict1 = staDict2
            staDict2 = statistcsGenerator(start_flag,end_flag,f)
            change_list.append(quantizationGenerator(staDict1,staDict2,target))
        count += 1
        start_flag += T
        if (end_flag + T) < end:
            end_flag += T
        else:
            end_flag = end
    print(change_list)
    return change_list
    Series(change_list).plot()

def event_with_match(comDict,evoDict,f,count,T):  #输入为社区字典、进化字典、连边的表格、时间窗序列号
    edges_info = pd.read_csv(f,low_memory=False,encoding='UTF-8')
    #event_about_match = DataFrame({'slot': [], 'group_id': [], 'm1': [], 'm2': [], 'm3': [], 'event': []})
    event_about_match = DataFrame({'slot': [], 'match_type': [], 'event': [], 'count': []})
    #先筛选出在时间窗内的记录
    start = 1431705600+T*(count-2)
    end = start+T
    match_dataframe1 = edges_info.loc[
        ((edges_info['start_time'] >= start) & (edges_info['start_time'] <= end))]
    match_dataframe2 = edges_info.loc[
        ((edges_info['close_time'] >= start) & (edges_info['close_time'] <= end))]
    match_dataframe3 = edges_info.loc[
        ((edges_info['start_time'] <= start) & (edges_info['close_time'] >= end))]  # 根据起始时间戳将时间窗内的数据筛选出来
    edges_info = (match_dataframe1.append(match_dataframe2, ignore_index=True)).append(match_dataframe3,ignore_index=True)
    edges_info.drop_duplicates()
    for key in comDict:   #对每一个社区统计
        match_type_count = {1:0,2:0,3:0}  # 1：线下有奖   2：线上有奖   3：无奖
        val = comDict[key]
        keyInStr = 'c' + str(count - 1) + str(key)
        event = community_evolution.decompose(evoDict[keyInStr][1])[0]
        for i in range(len(val)):
            for j in range(i+1,len(val)):
                node_first = val[i]
                node_second = val[j]
                temp_edge_info_target = edges_info.loc[edges_info['target'].isin([node_first])&(edges_info['source'].isin([node_second]))]
                temp_edge_info_source = edges_info.loc[edges_info['source'].isin([node_first])&(edges_info['target'].isin([node_second]))]
                if not temp_edge_info_target.empty:
                    match_type = Series(temp_edge_info_target['match_type'])
                    for index in temp_edge_info_source['match_type'].value_counts().index:
                        match_type_count[index] += temp_edge_info_source['match_type'].value_counts()[index]
                if not temp_edge_info_source.empty:
                    match_type = Series(temp_edge_info_source['match_type'])
                    for index in temp_edge_info_source['match_type'].value_counts().index:
                        match_type_count[index] += temp_edge_info_source['match_type'].value_counts()[index]
        print('match_type_count')
        print(match_type_count)
    return event_about_match






# f = '/users/xuan/PycharmProjects/untitled/match_information/match_table.csv'
# p = '/users/xuan/desktop/SNA/data/'
# statistcsGenerator(1482681600,1486310400,f)
# reward_change = quantizationInTimeline(1431705600,1557504000,5172240/2,f,'reward')
# person_limit_change = quantizationInTimeline(1431705600,1557504000,5172240/2,f,'person_limit')
# team_limit_change = quantizationInTimeline(1431705600,1557504000,5172240/2,f,'team_limit')
# Series(person_limit_change).to_csv(p+'person_limit_change.csv')
# Series(reward_change).to_csv(p+'reward_change.csv')
# Series(team_limit_change).to_csv(p+'team_limit.csv')
