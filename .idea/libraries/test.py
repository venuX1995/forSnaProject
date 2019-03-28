#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : test.py
# @Author: xuan
# @Date  : 2019-03-22
# @Desc  : for test
import pandas as pd
from pandas import DataFrame,Series
import numpy as np

dict1 = {'c11':{'c21':52,'c22':31,'c23':11},'c12':{'c21':13,'c22':15,'c23':19}}
dict1['c11']['c24'] = 27
print(dict1)