#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : graph.py
# @Author: xuan
# @Date  : 2019-02-18
# @Desc  : 1.generate a graph.
#          2.analyze the basic attributes.

import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import csv
import community
import pandas as pd
from pandas import Series,DataFrame
import tools
import community_evolution


def loadDataSet(fileName):
    data = np.load()
    return data


#def graphGenerator(edges):
    #G = nx.Graph()
    #G.add_edges_from(edges)
    #G.add_weighted_edges_from(edges)
    #return G

def graphDegree(G):
    #print("图的度分布为" + nx.degree_histogram(G))
    degree = nx.degree_histogram(G)
    x = range(len(degree))
    y = [z / float(sum(degree)) for z in degree]
    plt.loglog(x,y,color="blue",linewidth=2)
    plt.show()
    return nx.degree_histogram(G)

def graphClustering(G):
    print("图的平均聚集系数为" + str(nx.average_clustering(G)))
    return nx.average_clustering(G)

def graphDiameter(G):
    print("图的直径为" + str(nx.diameter(G)))
    return nx.diameter(G)

def graphCentrality(G):
    print("Degree Centrality" + str(nx.degree_centrality(G)))
    print("Closeness Centrality" + str(nx.closeness_centrality(G)))
    print("Betweenness Centrality" + str(nx.betweenness_centrality(G)))
    print("Eigenvector Centrality" + str(nx.eigenvector_centrality(G)))

def generate(f,start,end):   #根据给定的边文件筛选在时间窗[start，end）间的边，生成特定时间窗口内的静态图
    f_in = open(f, 'r')
    csv_reader = csv.reader(f_in, dialect='excel')
    G = nx.Graph()
    firstLine = True
    #print('G初始化')
    for line in csv_reader:
        if firstLine == True:
            firstLine = False
            continue
        startStamp = int(line[2])
        endStamp = int(line[3])  #起始的时间戳
        pplInTeam = int(line[4]) #具体的列数要根据数据源确定 这一项为队内的人数限制，目的为筛除超大型的队伍
        if((startStamp>=start and startStamp<end and pplInTeam<=100) or (endStamp>=start and endStamp<end and pplInTeam<=100)
                or (startStamp<start and endStamp>end and pplInTeam<=100)):
            #print('时间戳为：',line[2],' 所在比赛的每组人数限制为：',line[3])
            G.add_edge(line[0],line[1])
            #print('添加边：', line[0],'-',line[1])
    f_in.close()
    return G

#不规则划分时间窗产生静态网络。默认最小时间粒度为 T，比赛优先级 1>2>3，即线下>线上>无激励
def generateIrregularGraph(f,start,T): #输入边文件，以及此时间窗开始的时间戳，假定最小的时间窗粒度
    print('进入一个不规则时间窗建立过程')
    match_type_in_this_slot = priority_match_type(f,start,T)
    edges_in_this_slot = data_in_specific_window(f,start,T)
    next_is_same = True
    while next_is_same:
        start += T
        next_type = priority_match_type(f,start,T)
        if next_type==match_type_in_this_slot:
            print('与下一个时间窗最高优先级相同，下一个为：',next_type)
            edges_in_this_slot = edges_in_this_slot.append(data_in_specific_window(f,start,T))
        else:
            print('不一样，结束添加边')
            next_is_same = False
    G = nx.Graph()
    #建图
    for index,row in edges_in_this_slot.iterrows():
        G.add_edge(row['source'],row['target'])

    return G,start,match_type_in_this_slot


    # f_in = open(f, 'r')
    # csv_reader = csv.reader(f_in, dialect='excel')


#判断指定范围的数据行中最高的数据优先级，返回最高优先级、指定范围内的dataframe
def priority_match_type(f,start,T):
    edges_in_temp_slot = data_in_specific_window(f,start,T)
    match_type_default = '3'
    if 1 in list(edges_in_temp_slot['match_type'].values):
        match_type_default = '1'
    elif 2 in list(edges_in_temp_slot['match_type'].values):
        match_type_default = '2'
    print('这个时间窗的最高优先级比赛类型为：',match_type_default)
    #print('下一个时间窗口的最高优先级比赛类型为：',priority_match_type(f,start+T,T)[1])
    # if priority_match_type(f,start+T,T)[1]==match_type_default:
    #     print('进入递归')
    #     edges_in_temp_slot = edges_in_temp_slot.append(priority_match_type(f,start+T,T)[0],ignore_index=True)
    #     temp_end = priority_match_type(f,start+T,T)[2]
    return match_type_default


def data_in_specific_window(f,start,T):
    temp_start = start
    temp_end = start + T
    edges_in_temp_slot = pd.read_csv(f, low_memory=False, encoding='UTF-8-SIG')
    match_dataframe1 = edges_in_temp_slot.loc[
        ((edges_in_temp_slot['start_time'] >= start) & (edges_in_temp_slot['start_time'] <= temp_end))]
    match_dataframe2 = edges_in_temp_slot.loc[
        ((edges_in_temp_slot['close_time'] >= start) & (edges_in_temp_slot['close_time'] <= temp_end))]
    match_dataframe3 = edges_in_temp_slot.loc[
        ((edges_in_temp_slot['start_time'] <= start) & (
                edges_in_temp_slot['close_time'] >= temp_end))]  # 根据起始时间戳将时间窗内的数据筛选出来
    edges_in_temp_slot = (match_dataframe1.append(match_dataframe2, ignore_index=True)).append(match_dataframe3,
                                                                                               ignore_index=True)
    return edges_in_temp_slot


#基于比赛事件的窗口建立
def window_based_on_activity(df,mId): #f 是边的总文件，mID 是用于建立当前窗格的比赛 id
    edges = df.loc[df['match_id']==mId]
    G = nx.Graph()
    for index,row in edges.iterrows():
        G.add_edge(row['source'],row['target'])
    return G
#leadershipDF = community_evolution.getLeadershipOftime(G)
#print(community_evolution.getIndexInCommunity(50195,25,leadershipDF))

#drawing
#dendrogram = community.best_partition(G)

# for level in range(len(dendrogram) - 1) :
#     print("partition at level", level, "is", community.partition_at_level(dendrogram, level))
#graphDegree(G)
#graphCentrality(G)
#graphClustering(G)
