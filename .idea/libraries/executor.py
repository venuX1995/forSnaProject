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

p = '/users/xuan/desktop/SNA/data/'
f = p+'edges_with_timestamps.csv'


count = 1 #时间切片计数器
T: int = 5172240
start = 1431705600
endTimeStamp = 1538150400
end = start+T
dfOfNodeNum = DataFrame({'T_NO':[],'startDate':[],'endDate':[],'node_num':[]})   #初始化各个时间切片的节点数量、社区数量
dfOfComNum = DataFrame({'T_NO':[],'startDate':[],'endDate':[],'community_NO':[],'node_number_in_community':[],})
while end<endTimeStamp:        #建立不同的网络 并输出每个网络的节点总数及社区总数
    G = aboutGraph.generate(f,start,end)
    dfOfNodeNum=dfOfNodeNum.append((DataFrame({'T_NO':count,'startDate':tools.timeTrans(start,'%Y-%m-%d'),'endDate':tools.timeTrans(end,'%Y-%m-%d'),'node_num':nx.number_of_nodes(G)},index=[0])),ignore_index=True)
    print(dfOfNodeNum)
    comDict = community.best_partition(G)
    comDict = community_evolution.transformDict(comDict)
    for key,val in comDict.items():
        dfOfComNum = dfOfComNum.append((DataFrame({'T_NO': count, 'startDate':tools.timeTrans(start,'%Y-%m-%d'),'endDate':tools.timeTrans(end,'%Y-%m-%d'),'community_NO': key,'node_number_in_community':len(val),},index=[0])),ignore_index=True)
    print(dfOfComNum)
    print('count:',count,' start:',start,' end:',end)
    start += T
    if (end+T)<endTimeStamp:
        end +=T
    else:
        end = endTimeStamp
    count = count+1
dfOfNodeNum.to_csv(p+'nodeNum_of_T1.csv')
dfOfComNum.to_csv(p+'communityNum_of_T1.csv')