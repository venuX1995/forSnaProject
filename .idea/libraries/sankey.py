#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 17 14:44:43 2019

@author: yujia
"""
import pandas as pd
import json, urllib
import plotly.plotly as py
'''
scottish_df = pd.read_csv('/users/yujia/desktop/sankey.csv')
data_trace = dict(
    type='sankey',
    domain = dict(
      x =  [0,1],
      y =  [0,1]
    ),
    orientation = "h",
    valueformat = ".0f",
    node = dict(
      pad = 10,
      thickness = 30,
      line = dict(
        color = "black",
        width = 0
      ),
      label =  scottish_df['Node, Label'].dropna(axis=0, how='any'),
      color = scottish_df['Color']
    ),
    link = dict(
      source = scottish_df['Source'].dropna(axis=0, how='any'),
      target = scottish_df['Target'].dropna(axis=0, how='any'),
      value = scottish_df['Value'].dropna(axis=0, how='any'),
      color = scottish_df['Link Color'].dropna(axis=0, how='any'),
  )
)

layout =  dict(
    title = "Scottish Referendum Voters who now want Independence",
    height = 772,
    width = 950,
    font = dict(
      size = 10
    ),    
)

fig = dict(data=[data_trace], layout=layout)
plotly.offline.plot(fig, validate=False)
'''
import plotly.plotly as py
import plotly
p = '/users/xuan/desktop/SNA/data/'
i=100
plotly.offline.init_notebook_mode(connected=True)  # 在jupyter book中使用 
nodes = pd.read_csv(p+'community_index_noreward.csv',names = ['a','node'])
link = pd.read_csv(p+'data_4_sanky_noreward.csv')
data = dict(
    type='sankey',
    node = dict(
      label = nodes['node'].dropna(axis=0, how='any'),
      #color = ["blue", "blue", "green", "green", "black", "red"]
    ),
    link = dict(
      source = link['source'][0:i].dropna(axis=0, how='any'),
      target = link['target'][0:i].dropna(axis=0, how='any'),
      value = link['value'][0:i].dropna(axis=0, how='any'),
      label = link['label'][0:i].dropna(axis=0, how='any')
  ))

layout =  dict(title = "无激励比赛社区演化，以局部为例")
fig = dict(data=[data],layout=layout)     # 注意这里的data被转化为数据，可以支持同时绘制多个图形
plotly.offline.plot(fig, validate=False)
