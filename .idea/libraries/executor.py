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
f = p+'edges_with_timestamps20190411.csv'

count = 1 #时间切片计数器
T: int = 5172240
start = 1431705600
endTimeStamp = 1555084800
end = start+T
alpha = 0.3
beta = 0.3
gCur = nx.Graph()  #所有的演化计算需要在相邻的两个时间切片上进行，两个g分别代表当前时间切片及下一个时间切片
gPre = nx.Graph()
gNext = nx.Graph()
comDictNow,comDictPre,comDictNext = {},{},{}
diffDictPre,diffDictNext = {},{}
staDictNext: dict
staDictPre,staDictNext = {},{}
dataForVisual = DataFrame({'时间切片':[],'事件':[],'数量':[]})
leadership = pd.DataFrame({'nodeID':[],'community':[],'leadership_in_community':[]})
while end<endTimeStamp:        #循环建立每个静态网络 并输出每两个图之间的稳定性字典和差异性字典
    G = aboutGraph.generate(f,start,end)
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
        formingCount,mergingCount,growingCount,shrinkingCount,disolvingCount,splittingCount,continuingCount = 0,0,0,0,0,0,0
        for key,val in evoDict.items():
            for event in val:
                if event=='forming':
                    formingCount+=1
                elif event=='merging':
                    mergingCount+=1
                elif event=='growing':
                    growingCount+=1
                elif event=='shrinking':
                    shrinkingCount+=1
                elif event=='disolving':
                    disolvingCount+=1
                elif event=='splitting':
                    splittingCount+=1
                elif event=='continuing':
                    continuingCount+=1
        print(formingCount,' ',mergingCount)
        print(count)
        dataForVisual=dataForVisual.append(DataFrame({'时间切片':[count-1],'事件':['forming'],'数量':[formingCount]}),ignore_index=True)
        dataForVisual=dataForVisual.append(DataFrame({'时间切片': [count-1], '事件': ['merging'], '数量': [mergingCount]}), ignore_index=True)
        dataForVisual=dataForVisual.append(DataFrame({'时间切片': [count-1], '事件': ['growing'], '数量': [growingCount]}), ignore_index=True)
        dataForVisual=dataForVisual.append(DataFrame({'时间切片': [count-1], '事件': ['shrinking'], '数量': [shrinkingCount]}), ignore_index=True)
        dataForVisual=dataForVisual.append(DataFrame({'时间切片': [count-1], '事件': ['disolving'], '数量': [disolvingCount]}), ignore_index=True)
        dataForVisual=dataForVisual.append(DataFrame({'时间切片': [count-1], '事件': ['splitting'], '数量': [splittingCount]}), ignore_index=True)
        dataForVisual=dataForVisual.append(DataFrame({'时间切片': [count-1], '事件': ['continuing'], '数量': [continuingCount]}), ignore_index=True)
        print(dataForVisual)
    start += T
    if (end+T)<endTimeStamp:
        end +=T
    else:
        end = endTimeStamp
    count = count+1
dataForVisual.to_csv(p+'data_to_visualization.csv')
leadershipToGroup = leadership['leadership_in_community'].groupby(leadership['nodeID'])
print(leadershipToGroup)
leadershipToGroup.mean().to_csv(p+'avgLeadership.csv')
#leadership.to_csv(p+'leadershipOfAll.csv')