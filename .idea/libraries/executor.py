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

p = '/users/xuan/desktop/SNA/data/'
f = p+'edges_with_timestamps.csv'

count = 1 #时间切片计数器
T: int = 5172240
start = 1431705600
endTimeStamp = 1538150400
end = start+T
# dfOfNodeNum = DataFrame({'T_NO':[],'startDate':[],'endDate':[],'node_num':[]})   #初始化各个时间切片的节点数量、社区数量
# dfOfComNum = DataFrame({'T_NO':[],'startDate':[],'endDate':[],'community_NO':[],'node_number_in_community':[],})
gCur = nx.Graph()  #所有的演化计算需要在相邻的两个时间切片上进行，两个g分别代表当前时间切片及下一个时间切片
gPre = nx.Graph()
gNext = nx.Graph()
comDictNow,comDictPre,comDictNext = {}
diffDictPre,diffDictNext = {}
staDictPre,staDictNext = {}
while end<endTimeStamp:        #循环建立每个静态网络 并输出每两个图之间的稳定性字典和差异性字典
    G = aboutGraph.generate(f,start,end)
    #dfOfNodeNum=dfOfNodeNum.append((DataFrame({'T_NO':count,'startDate':tools.timeTrans(start,'%Y-%m-%d'),'endDate':tools.timeTrans(end,'%Y-%m-%d'),'node_num':nx.number_of_nodes(G)},index=[0])),ignore_index=True)
    #print(dfOfNodeNum)
    # comDict = community.best_partition(G)
    # comDict = community_evolution.transformDict(comDict)
    # for key,val in comDict.items():
    #     dfOfComNum = dfOfComNum.append((DataFrame({'T_NO': count, 'startDate':tools.timeTrans(start,'%Y-%m-%d'),'endDate':tools.timeTrans(end,'%Y-%m-%d'),'community_NO': key,'node_number_in_community':len(val),},index=[0])),ignore_index=True)
    # # print(dfOfComNum)
    # # print('count:',count,' start:',start,' end:',end)
    # if (count is 19) or (count is 20):
    #     print(comDict)
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
        comDictNext = community_evolution.transformDict(community.best_partition(gNext))
        staDict = community_evolution.computeStability(dic1,dic2,count)
        # with open(p+'dictionary/'+'staDict'+str(count)+'.csv','w+') as f_out1:
        #     for key,val in staDict.items():
        #         f_out1.write(key+"\t"+json.dumps(val,ensure_ascii=False))
        #         print("将字典写入文件……")
        #         f_out1.write("\n")
        diffDict = community_evolution.computeDifference(gCur,gNext,dic1,dic2,count)
        # with open(p+'dictionary/'+'diffDict'+str(count)+'.csv','w+') as f_out2:
        #     for key,val in diffDict.items():
        #         f_out2.write(key+"\t"+json.dumps(val,ensure_ascii=False))
        #         print("将字典写入文件……")
        #         f_out2.write("\n")
        # print("稳定性字典为：")
        # print(staDict)
        # print("差异性字典为：")
        # print(diffDict)
    start += T
    if (end+T)<endTimeStamp:
        end +=T
    else:
        end = endTimeStamp
    count = count+1
