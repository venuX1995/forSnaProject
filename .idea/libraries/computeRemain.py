#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : computeRemain.py
# @Author: xuan
# @Date  : 2019-06-14
# @Desc  :
import xlrd
from openpyxl import load_workbook
from openpyxl import Workbook
import pandas as pd
from pandas import Series,DataFrame
import  sys
p = '/users/xuan/desktop/SNA/data/'
f = '/users/xuan/desktop/SNA/data/Original/20190410.csv'
data = pd.read_csv(f)
match_remain_population = DataFrame({'match_id':[],'population':[],'remain_population':[],'remain_percent':[]})
first_match_data = DataFrame({'user_id':[],'first_match':[]})
match_id = Series(data['match_id'].unique())
user_id = Series(data['user_id']).unique()
for id in user_id:
    all_match_for_user = list(data.loc[data['user_id']==id].match_id)
    first_match = min(all_match_for_user)
    first_match_data = first_match_data.append(DataFrame({'user_id':[id],'first_match':[first_match]}))
first_match_data.to_csv(p+'first_match_data.csv')

for index,mid in match_id.iteritems():
    if index<=len(match_id)-4:
        match_next_one = match_id[index+1]
        match_next_two = match_id[index+2]
        match_next_three = match_id[index+3]
        population_in_now = set(list(data.loc[data['match_id']==mid].user_id))
        population_in_next = set(list(data.loc[data['match_id']==match_next_one].user_id)).union\
            (set(list(data.loc[data['match_id']==match_next_two].user_id)),set(list(data.loc[data['match_id']==match_next_three].user_id)))
        remain_population = population_in_next.intersection(population_in_now)
        match_remain_population=match_remain_population.append(DataFrame({'match_id':[mid],'population':[len(population_in_now)],
                                                                          'remain_population':[len(remain_population)],
                                                                          'remain_percent':[len(remain_population)/len(population_in_now)]}))
print(match_remain_population)
match_remain_population.to_csv(p+'match_remain_population.csv')
