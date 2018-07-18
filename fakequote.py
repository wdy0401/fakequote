# -*- coding: utf-8 -*-
"""
Created on Tue Jul 10 09:42:05 2018

@author: admin
"""


import pandas as pd
import pathlib
import random


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
class stock(object):
    def __init__(self):
        pass
    def set_ctr(self,ctr):
        ctr=str(ctr)
        if(ctr[0:3]=='600' or ctr[0:3]=='601'):
            self.mkt=1#SH
        elif(ctr[0:3]=='000' or ctr[0:3]=='002' or ctr[0:3]=='300'):
            self.mkt=2#SZ
        else:
            raise ValueError("ERROR stock code "+str(ctr))
        self.ctr=ctr
    def set_date_range(self,dates):
        for dt in dates:
            fname=self.gen_file_name(dt)
            if not pathlib.Path(fname).is_file():
                raise ValueError("File not exist "+fname)
        self.dates=dates
    def load_histroy(self):
        pdlist=list()    
        for dt in self.dates:
            fname=self.gen_file_name(dt)
            a=pd.read_csv(fname,parse_dates=True,encoding="GBK")
            a.index=[pd.Timestamp(str(a['TradingDay'][x])+" "+str(a['UpdateTime'][x])+','+str(a['UpdateMillisec'][x])) for x in range(len(a))]
            pdlist.append(a)
        self.raw_pd=pd.concat(pdlist)
    def time_grep(self):        #omit open close auction
        self.pd=self.raw_pd.copy()
        self.pd['grep']=self.pd.index
        self.pd['grep']=self.pd['grep'].apply(self.trading_time_grep)
        self.pd=self.pd[self.pd['grep']!=0]
    def time_select(self):
        #gen random selected k bars from total m bars
        #k different from 
        #   exchange    close auction
        #   pre      tick or 1minbar or etc
        if self.mkt==1:
            self.bar_num=20*60*4+2
        elif self.mkt==2:
            self.bar_num=20*(60*4-3)+2
        sortlist=list(range(len(self.df)))
        random.shuffle(sortlist)
        sortlist=sortlist[0:self.bar_num]
        sortlist.sort()
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
        #volume adjust by random(0.9,1.1) 
        pass
    def gen_file_name(self,dt):
        return f"./data/md/{dt}/{self.ctr}_{self.mkt}.bak.csv"
    def trading_time_grep(self,x):
        if ((x.hour==9 and x.minute>29) \
            or (x.hour==10) \
            or (x.hour==11 and x.minute<31) \
            or (x.hour==13) \
            or (self.mkt==1 and x.hour==14) \
            or (self.mkt==2 and x.hour==14 and x.minute<57) \
            or (self.mkt==2 and x.hour==14 and x.minute==57 and x.second==0) \
            
            ):#open close auction(x.hour==9 and x.minute==25)  (x.hour==15 and x.minute==0)
            
            return x
        else:
            return 0
    
c=stock()
c.set_ctr("600000")
c.set_date_range([20180102,20180103])
c.load_histroy()
c.time_grep()
c.time_select()
x=c.pd
'''
生成nbbo
空值就是,,
'''