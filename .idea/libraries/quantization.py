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

#统计不同的激励措施在各个时间窗口上的指标值（ppl_in_team/team_limit/awards)
#最终得出的应该是以激励措施和激励措施下面的具体划分为双索引（或者加上激励措施下面的具体划分成为三索引？）的字典
def statistcsGenerator(start,end,f):#输入为时间窗起始时间、match_table
    # f_in = open(f, 'r')
    # csv_reader = csv.reader(f_in, dialect='excel')
    match_dataframe = pd.read_csv(f,low_memory=False,encoding='GB2312')
    statisticsDict = {'person_limit':[],'team_limit':[],'reward':[]}
    #TODO：这里的窗格筛选条件写的还有问题
    match_dataframe = match_dataframe.loc[((match_dataframe['start_time']>=start)&(match_dataframe['start_time']<=end))]#根据起始时间戳将时间窗内的数据筛选出来
    #1.计算队内人数的限制
    statisticsDict['person_limit'] = match_dataframe['ppl_in_team'].value_counts() #以series的形式存储在字典中
    #2.计算队伍数量的限制
    statisticsDict['team_limit'] = match_dataframe['team_limit'].value_counts()
    #3.计算激励措施的情况
    statisticsDict['reward'] = match_dataframe['binary_award'].value_counts()
    print(statisticsDict)
    print(statisticsDict['person_limit'].index)
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
        if count==1:
            staDict1 = statistcsGenerator(start_flag,end_flag,f)
        if count==2:
            staDict2 = statistcsGenerator(start_flag,end_flag,f)
            change_list.append(quantizationGenerator(staDict1,staDict2,target))
        else:
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
    Series(change_list).plot()






f = '/users/xuan/PycharmProjects/untitled/match_information/match_table.csv'
statistcsGenerator(1482681600,1486310400,f)