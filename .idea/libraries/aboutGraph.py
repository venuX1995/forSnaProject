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
    #print('G初始化')
    for line in csv_reader:
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


#leadershipDF = community_evolution.getLeadershipOftime(G)
#print(community_evolution.getIndexInCommunity(50195,25,leadershipDF))

#drawing
#dendrogram = community.best_partition(G)

# for level in range(len(dendrogram) - 1) :
#     print("partition at level", level, "is", community.partition_at_level(dendrogram, level))
#graphDegree(G)
#graphCentrality(G)
#graphClustering(G)
