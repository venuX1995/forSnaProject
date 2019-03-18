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

p = '/users/xuan/desktop/SNA/data/'
f_in = open(p+'edges.csv', 'r')
G = nx.Graph()
csv_reader = csv.reader(f_in,dialect='excel')
for line in csv_reader:
    G.add_edge(line[0],line[1])
f_in.close()
leadershipDF = community_evolution.getLeadershipOftime(G)
print(community_evolution.getIndexInCommunity(50195,25,leadershipDF))

#drawing
#dendrogram = community.best_partition(G)

# for level in range(len(dendrogram) - 1) :
#     print("partition at level", level, "is", community.partition_at_level(dendrogram, level))
#graphDegree(G)
#graphCentrality(G)
#graphClustering(G)
