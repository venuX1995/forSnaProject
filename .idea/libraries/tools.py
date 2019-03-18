#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : tools.py
# @Author: xuan
# @Date  : 2019-03-04
# @Desc  : tools etc.
import csv
import pandas as pd
from pandas import Series,DataFrame
import  sys
import datetime,time
from datetime import  date,datetime,timedelta

def cleanDuplicateData(f,export):
    f_in = open(f, 'r')
    f_out = open(export, 'w', newline='')
    csv_reader = csv.reader(f_in, dialect='excel')
    csv_writer = csv.writer(f_out, dialect='excel')
    for line in csv_reader:
        if line[0] != line[1]:
            csv_writer.writerow(line)
    f_in.close()
    f_out.close()

def cleanInvalidData(f,export):
    f_in = open(f,'r')
    f_out = open(export,'w',newline='')
    csv_reader = csv.reader(f_in,dialect='excel')
    csv_writer = csv.writer(f_out,dialect='excel')
    for line in csv_reader:
        if line['team_limit'] != 1:
            csv_writer.writerow(line)
    f_in.close()
    f_out.close()

def createEdges(f,export):
    f_in = open(f,'r')
    export = open(export,'w')
    csv_reader = csv.reader(f_in,dialect='excel')
    csv_writer = csv.writer(export,dialect='excel')

def timeTrans(timeStamp,format):
    formatTime = time.strftime(format,time.localtime(timeStamp))
    return formatTime

def dict2csv(dict,file):
    com = DataFrame({'Node':[],'Community':[]})
    for key in dict:
        com = com.append(DataFrame({'Node':key,'Community':dict[key]},index=[0]))
    com.to_csv(file)
print(timeTrans(1552533694,"%Y-%m-%d %H:%M:%S"))
print(timeTrans(1552572090,"%Y-%m-%d %H:%M:%S"))
print(timeTrans(1552576162,"%Y-%m-%d %H:%M:%S"))
print(timeTrans(1551505121,"%Y-%m-%d %H:%M:%S"))