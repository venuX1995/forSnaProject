import sys
import pandas as pd
from pandas import Series,DataFrame
import networkx as nx


p = '/users/xuan/desktop/SNA/data/志愿者人脸相关数据/人脸/'
f = p+'picture_people_match1.csv'
export = p+'afterClean.csv'
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
