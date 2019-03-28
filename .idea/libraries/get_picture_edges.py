#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : get_picture_edges.py
# @Author: xuan
# @Date  : 2019-03-21
# @Desc  : get network from pictures.
import sys
import pandas as pd
from pandas import Series,DataFrame
import networkx as nx
import csv
import operator

p = '/users/xuan/desktop/SNA/data/志愿者人脸相关数据/人脸/'
f = p+'picture_people_match2.csv'
export = p+'afterClean.csv'
f_out = p+'edges2.csv'
def cleanInvalidData(f,export):      #清除无名数据
    f_in = open(f,'r')
    f_out = open(export,'w',newline='')
    csv_reader = csv.reader(f_in,dialect='excel')
    csv_writer = csv.writer(f_out,dialect='excel')
    for line in csv_reader:
        print(line)
        if not operator.eq(line[1],'unknown'):   #jaccount与unknown对比
            print(line)
            csv_writer.writerow(line)
    f_in.close()
    f_out.close()

def get_edges(f_in,f_out):           #输出两两组合之间的组队次数
    user_and_team_info = pd.read_csv(f_in)
    user_id = Series(user_and_team_info.jaccount).unique()
    get_team_times = DataFrame({'fellow_id': [], 'times': [], 'user_id': []})
    for id in user_id:
        team = user_and_team_info.loc[user_and_team_info['jaccount'].isin([id])]
        if not (team.empty):
            all_friends = user_and_team_info.loc[user_and_team_info['pic_name'].isin(team.pic_name)]
            friend_times = DataFrame({'fellow_id': all_friends['jaccount'].value_counts().index,
                                      'times': all_friends['jaccount'].value_counts().values})
            friend_times['user_id'] = id
            get_team_times = get_team_times.append(friend_times, ignore_index=True)
    # get_team_times = get_team_times.drop(get_team_times['fellow_id']==get_team_times['user_id'])
    get_team_times = get_team_times.set_index(['user_id'])
    get_team_times.columns = ['source','target','weight']

    get_team_times.to_csv(f_out)

cleanInvalidData(f,export)
get_edges(export,f_out)
