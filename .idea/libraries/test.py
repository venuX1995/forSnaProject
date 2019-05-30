#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : test.py
# @Author: xuan
# @Date  : 2019-03-22
# @Desc  : for test
import pandas as pd
from pandas import DataFrame,Series
import numpy as np
import tools
import csv
import chardet
import os
import time
from openpyxl import load_workbook
from openpyxl import Workbook

# def check_file_charset(file):
#     with open(file,'rb') as f:
#         return chardet.detect(f.read())
# print(check_file_charset('/users/xuan/desktop/SNA/data/data_to_visualization.csv'))
def decompose(nextState):
    nextComList = []
    tempList = nextState.split(' ')
    event = tempList[0]
    nextComList = tempList[1].split(',')
    return event,nextComList

string = 'splittingTo '+'C11,C22,C33,C44'
event,nextComList = decompose(string)
print(event)
print(nextComList)
while len(nextComList)!=2:
    nextComList.pop()
print(nextComList)
# p = '/users/xuan/desktop/SNA/data/Original/'
# wb_in = load_workbook(p+'20190410.xlsx')
# ws_in = wb_in.get_sheet_by_name('20190410')
# print(ws_in)
# team_info = {}
# edges_count = 0
# for i in range(2, ws_in.max_row):
#     team_id = ws_in.cell(i, 2).value
#     if team_info.__contains__(team_id) == False:
#         team_info[team_id] = []
#     team_info[team_id].append(ws_in.cell(i, 1).value)
#
# # 输出'NoneType' object has no attribute
# wb_out = Workbook()
# ws_out = wb_out.active
# ws_out.append(['source', 'target', 'team_id'])
# for key in team_info.keys():
#     team_members = team_info[key]
#     team_len = len(team_info[key])
#     # print(team_len, team_members)
#     handshake_count = 0
#     if (team_len > 1)&(team_len < 50):
#         for i in range(0, team_len):
#             for j in range(i + 1, team_len):
#                 # print(i, j, [team_members[i], team_members[j], key])
#                 ws_out.append([team_members[i], team_members[j], key])
#                 handshake_count += 1
#     edges_count += handshake_count
#     print('team_id:', key, ' team_len:', team_len, ' handshakes:', handshake_count)
# print("共计形成边：",edges_count)
# wb_out.save(p+'edegs20190411.xlsx')


#print(tools.timeTrans(1556152269,"%Y-%m-%d %H:%M:%S"))
#print(tools.timeTrans(1556221190,"%Y-%m-%d %H:%M:%S"))