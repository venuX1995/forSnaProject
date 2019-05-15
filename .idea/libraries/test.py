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

def check_file_charset(file):
    with open(file,'rb') as f:
        return chardet.detect(f.read())
print(check_file_charset('/users/xuan/PycharmProjects/untitled/match_information/match_table.csv'))
# def read_file_as_str(file_path):
#     # 判断路径文件存在
#     if not os.path.isfile(file_path):
#         raise TypeError(file_path + " does not exist")
#
#     all_the_text = open(file_path).read()
#     # print type(all_the_text)
#     return all_the_text
#
# def findReward(textStr):
#     if ('奖励' in textStr) or ('获得' in textStr):
#         return 1
#     else:
#         return 0
#
#
# f = './match_information/match_tableSplit.csv'
# f_in = open(f, 'r')
# csv_reader = csv.reader(f_in, dialect='excel')
# for line in csv_reader:
#     match_id = str(line[0])
#     file_path = 'match_information/matches/'+match_id+'.txt'
#     match_info_text = read_file_as_str(file_path)
#     existReward = findReward(match_info_text)
#     print(match_id+'号比赛的奖励情况'+existReward)

#print(tools.timeTrans(1556152269,"%Y-%m-%d %H:%M:%S"))
#print(tools.timeTrans(1556221190,"%Y-%m-%d %H:%M:%S"))