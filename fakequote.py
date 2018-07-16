# -*- coding: utf-8 -*-
"""
Created on Tue Jul 10 09:42:05 2018

@author: admin
"""

'''
faketime   oritime    method
9-10       9-11       压缩
9-10       9-9.5      拉伸
9-10       10-11      删除
'''
from datetime import datetime
import pandas as pd

#b=pd.Timestamp("2018-04-02 09:20:15,554").to_pydatetime()

'''
按时间段进行价格处理
处理后进行拼接
拼接注意事项:    
    在有删除操作时 保证拼接处的收益率
    价格不超过涨跌停
    成交量符合U型曲线

输入:
    待生成日
    源数据日序列
    源数据颗粒度需不大于需求精度
输出:
    按指定精度给出的行情数据
    源数据颗粒度需不大于指定精度
    
细节:
    先看old超出new部分有多少
   T 超出部分的量通过删掉1/2 压缩1/2进行处理 可以调节压缩删除比例
    删除压缩区别在于  删除是整段数据 也就是数个bar 多个bar合成一个bar
    现在均采取删除的方式  也就是m个k线里面取n个
    arr = np.arange(10)
    np.random.shuffle(arr)
    arr
    
    先把源数据粒度统一成需求精度
    
    成交量需要添加微幅波动
    集合竞价成交量也需要按添加微幅波动 以免可与日期对应
    如何将集合竞价数据统一成k线数据 
    
'''

class time_map(object):
    # pre: day 1min 6sec 500ms
    def set_pre(self,pre):
        self.pre=pre
    pass


class stock(object):
    def load_histroy(self):
        #load every day
        #merge to one dataframe
        pass
    def pre_convert(self):
        #day to standard bar
        #deal open close auction
        pass
    def time_select(self):
        #gen random selected k bars from total m bars
        #k different from 
        #   exchange    close auction
        #   pre      tick or 1minbar or etc
        pass
    def conbine_bar(self):
        #conbine bars with time select
        #get open from pre set info or determined from today ohlc
        #keep inter bar return(between ori and fake) 
        pass
    def hl_limit_adj(self):
        #get last settlement price
        #cut price which is higher or lower than limit
        pass
    def volume_adj(self):
        #9:30-10:00 adj
        #14:50-15:00 adj
        #ratio=(the openclose bar)/(average of none openclose bar)
        pass
    def auction_adj(self):
        #9:25 for sh sz
        #15:00 for sz
        pass


a=pd.read_csv("./data/md/20180102/000001_2.bak.csv",parse_dates=True)
a.index=[pd.Timestamp(str(a['TradingDay'][x])+" "+str(a['UpdateTime'][x])) for x in range(len(a))]

a=pd.read_csv("./data/md/20180102/600000_1.bak.csv",parse_dates=True,encoding="GBK")
a.index=[pd.Timestamp(str(a['TradingDay'][x])+" "+str(a['UpdateTime'][x])) for x in range(len(a))]

