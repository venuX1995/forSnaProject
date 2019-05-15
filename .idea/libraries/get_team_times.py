#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : get_team_times.py
# @Author: xuan
# @Date  : 2018/10/17
# @Desc  :

import pandas as pd
from pandas import Series,DataFrame
import  sys

p = '/users/xuan/desktop/SNA/data/Original/'
user_and_team_info = pd.read_csv(p+'player_table.csv')
user_id = Series(user_and_team_info.user_id).unique()
get_team_times = DataFrame({'fellow_id':[],'times':[],'user_id':[]})
for id in user_id:
    id = str(id)
    team = user_and_team_info.loc[user_and_team_info['user_id'].isin([id])]
    if not (team.empty):
        all_friends = user_and_team_info.loc[user_and_team_info['team_id'].isin(team.team_id)]
        friend_times = DataFrame({'fellow_id':all_friends['user_id'].value_counts().index,'times':all_friends['user_id'].value_counts().values})
        friend_times['user_id'] = id
        get_team_times = get_team_times.append(friend_times,ignore_index=True)
#get_team_times = get_team_times.drop(get_team_times['fellow_id']==get_team_times['user_id'])
get_team_times = get_team_times.set_index(['user_id'])

get_team_times.to_csv(p+'get_team_times20190411.csv')
