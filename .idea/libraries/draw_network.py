#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : draw_network.py
# @Author: xuan
# @Date  : 2018/10/18
# @Desc  : draw social network

import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd

p = '/users/xuan/desktop/SNA研究/data/'
G = nx.Graph()
for line in open(p+'user_id.csv'):
    G.add_node(line)
for line in open((p+'get_team_times.csv')):
    line = line.split(',')
    n1 = line[0]
    n2 = line[1]
    w = line[2]
    G.add_edge(n1,n2,weight=w)
#G.add_nodes_from([1,2,3,4,5,7,9])
#G.add_edges_from([(1,2),(2,3),(1,9),(2,5)])
nx.draw(G,node_size=5,node_color='#A0CBE2',width=1,edge_cmap=plt.cm.Blues,with_labels=False,pos=nx.spring_layout(G,scale=2))
plt.show()
