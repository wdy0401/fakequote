# -*- coding: utf-8 -*-
"""
Created on Tue Jul 10 09:42:05 2018

@author: admin
"""


import pandas as pd
import numpy as np
import pathlib
import random
from datetime import datetime
import matplotlib.pyplot as plt
from functools import reduce,wraps

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


    成交量需要添加微幅波动
    集合竞价成交量也需要按添加微幅波动 以免可与日期对应
    如何将集合竞价数据统一成k线数据

'''
def betimer(func):
    @wraps(func)
    def wrapper(*args, **kw):
        btime=datetime.now()
        ret=func(*args, **kw)
        dift=datetime.now()-btime
        print('%s %s' % (func.__name__ , dift))
        return ret
    return wrapper

class stock(object):
    def __init__(self):
        pass
    def set_today(self,date):
        self.today=date
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
    def set_pre_close(self,price):
        self.pre_close=price
    def set_price_level(self,level):
        self.price_level=level
    @betimer
    def load_histroy(self):
        pdlist=list()
        for dt in self.dates:
            fname=self.gen_file_name(dt)
            a=pd.read_csv(fname,parse_dates=True,encoding="GBK")
            a.index=[pd.Timestamp(str(a['TradingDay'][x])+" "+str(a['UpdateTime'][x])+','+str(a['UpdateMillisec'][x])) for x in range(len(a))]
            pdlist.append(a)
        self.raw_df=pd.concat(pdlist)
    @betimer
    def time_grep(self):        #omit open close auction
        self.clean_df=self.raw_df.copy()
        self.clean_df['grep']=self.clean_df.index
        self.clean_df['grep']=self.clean_df['grep'].apply(self.trading_time_grep)
        self.clean_df=self.clean_df[self.clean_df['grep']!=0]
        self.clean_df=self.clean_df.drop_duplicates(subset='grep')
    @betimer
    def time_select(self):
        #gen random selected k bars from total m bars
        #每次取20个 丢掉n个 尽量取满整个数据段
        if self.mkt==1:
            self.bar_num=20*60*4+2
        elif self.mkt==2:
            self.bar_num=20*(60*4-3)+2
        sortlist=list(range(len(self.clean_df)))
        random.shuffle(sortlist)
        sortlist=sortlist[0:self.bar_num]
        sortlist.sort()
        self.sortlist=sortlist
        #self.sortlist=list(filter(lambda x:int(int(x/20)%2)==1,range(len(self.clean_df))))
        self.sortlist=list(filter(lambda x: x%(int(20*len(self.clean_df)/self.bar_num))<20,range(len(self.clean_df))))
        self.sortlist=self.sortlist[0:self.bar_num]
    @betimer
    def conbine_bar(self):
        #conbine bars with time select
        #get open from pre set info or determined from today ohlc
        #keep inter bar delta(price)(between ori and fake)
        #本质上就是选了n个相邻tick的价格变化 通过这n个价格变化关系重构价格序列
        self.df=self.clean_df.copy()
        tail_tag="_next"
        columns=['BidPrice1']
        add=lambda x,y:x+y
        self.item_list=reduce(add,[[str(t)+str(s+1) for t in reduce(add,[[i+j for i in ["Bid",'Ask']] for j in ["Price",'Volume']])] for s in range(self.price_level)]);
        item_list=self.item_list
        item_dict=dict(enumerate(item_list))
        item_dict_r= {v:k for k,v in item_dict.items()}
        y=self.df.loc[:,item_list]
        y0=self.df.loc[:,['BidPrice1']]
        y0.columns=columns
        y1=y0[1:]
        y1.index=y0.index[0:-1]
        y1.columns=[str(x)+tail_tag for x in columns]
        y2=pd.concat([y0,y1],axis=1)
        y3=y2.iloc[self.sortlist]

        ph=dict()
        lastp=0
        pdif=0

        ph['BidPrice1']=list()
        for i,j in enumerate(y3.index):
            if i==0:
                ph['BidPrice1'].append(y3.loc[j,'BidPrice1'])
            else:
                ph['BidPrice1'].append(lastp+pdif)
            pdif=y3.loc[j,'BidPrice1'+tail_tag]-y3.loc[j,'BidPrice1']
            lastp=ph['BidPrice1'][-1]
        ph['BidPrice1']=[round(x,2) for x in ph['BidPrice1']]

        for price in item_list:
            if "BidPrice1" in price:
                continue
            else:
                ph[price]=list()
                if "Volume" in price:
                    for i in range(len(ph['BidPrice1'])):
                        ph[price].append(y.iloc[i,item_dict_r[price]])
                else:
                    for i in range(len(ph['BidPrice1'])):
                        ph[price].append(round(ph["BidPrice1"][i]+y.iloc[i,item_dict_r[price]]-y.iloc[i,0],2))
        self.ph=ph
        self.df=pd.DataFrame(ph,index=y3.index)
        self.df['ori_index']=self.df.index
    @betimer
    def timestamp_adj(self):
        #convert index to 930-1500
        #14:50-15:00 adj
        list_morning=[i*pd.Timedelta('3s')+pd.Timestamp(str(self.today)+" 9:30:00") for i in range(20*60*2+1)]
        list_afternoon=list()
        if self.mkt==1:
            list_afternoon=[i*pd.Timedelta('3s')+pd.Timestamp(str(self.today)+" 13:00:00") for i in range(20*60*2+1)]
        else:
            list_afternoon=[i*pd.Timedelta('3s')+pd.Timestamp(str(self.today)+" 13:00:00") for i in range(20*60*2+1-3*20)]
        self.time_list=list_morning+list_afternoon
        self.df.index=self.time_list
    @betimer
    def hl_limit_adj(self):
        pc=0
        if hasattr(self,'pre_close'):
            pc=self.pre_close
            print(pc,1)
        else:
            tmp=self.df.iloc[0,:]
            pc=round((tmp['BidPrice1']*tmp['BidVolume1']+\
                     tmp['AskPrice1']*tmp['AskVolume1'])/(\
                        tmp['BidVolume1']+tmp['AskVolume1']),2)
            #pc=round(((tmp['BidPrice1']+tmp['AskPrice1'])/2),2)
            print(pc,2)
        self.high_limit=round(pc*1.1,2)
        self.high_limit=12.7
        self.low_limit=round(pc*0.9,2)
        for ind in self.df.index:
            #bid part
            needfix=0
            for i in range(self.price_level):#对每个价位做调整
                bp=self.df.loc[ind,'BidPrice'+str(i+1)]
                if bp<self.low_limit:#小于跌停板的买价 全部删除
                    for j in range(i,self.price_level):
                        self.df.loc[ind,'BidPrice'+str(j+1)]=0
                        self.df.loc[ind,'BidVolume'+str(j+1)]=0
                    break
                elif bp>self.high_limit:#大于涨停板的买价 需要保留量的信息
                    if i<self.price_level-1:#可以往下放
                        if self.df.loc[ind,'BidPrice'+str(i+2)]>=self.high_limit:#下面接得住
                            needfix+=1
                            self.df.loc[ind,'BidVolume'+str(i+2)]+=self.df.loc[ind,'BidVolume'+str(i+1)]
                            self.df.loc[ind,'BidPrice'+str(i+1)]=0
                            self.df.loc[ind,'BidVolume'+str(i+1)]=0
                        else:#下面接不住 就地变成涨停板
                            self.df.loc[ind,'BidPrice'+str(i+1)]=self.high_limit
                    else:#无法往下放 就地变成涨停板
                            self.df.loc[ind,'BidPrice'+str(i+1)]=self.high_limit
            #针对可能出现的有level2没有level1的情况 重新对bid进行赋值
            if needfix>0:
                for i in range(self.price_level-needfix):#对每个价位做调整
                    self.df.loc[ind,'BidPrice'+str(1+i)]=self.df.loc[ind,'BidPrice'+str(i+1+needfix)]
                    self.df.loc[ind,'BidVolume'+str(1+i)]=self.df.loc[ind,'BidVolume'+str(i+1+needfix)]
                for i in range(needfix):#删除不需要价位
                    self.df.loc[ind,'BidPrice'+str(self.price_level-i)]=0
                    self.df.loc[ind,'BidVolume'+str(self.price_level-i)]=0


            #ask part
            needfix=0
            for i in range(self.price_level):#对每个价位做调整
                ap=self.df.loc[ind,'AskPrice'+str(i+1)]
                if ap>self.high_limit:#大于涨停板的卖价 全部删除
                    for j in range(i,self.price_level):
                        self.df.loc[ind,'AskPrice'+str(j+1)]=0
                        self.df.loc[ind,'AskVolume'+str(j+1)]=0
                    break
                elif ap<self.low_limit:#小于跌停板的卖价 需要保留量的信息
                    if i<self.price_level-1:#可以往下放
                        if self.df.loc[ind,'AskPrice'+str(i+2)]<=self.low_limit:#下面接得住
                            needfix+=1
                            self.df.loc[ind,'AskVolume'+str(i+2)]+=self.df.loc[ind,'AskVolume'+str(i+1)]
                            self.df.loc[ind,'AskPrice'+str(i+1)]=0
                            self.df.loc[ind,'AskVolume'+str(i+1)]=0
                        else:#下面接不住 就地变成跌停板
                            self.df.loc[ind,'AskPrice'+str(i+1)]=self.low_limit
                    else:#无法往下放 就地变成涨停板
                            self.df.loc[ind,'AskPrice'+str(i+1)]=self.low_limit
            #针对可能出现的有level2没有level1的情况 重新对ask进行赋值
            if needfix>0:
                for i in range(self.price_level-needfix):#对每个价位做调整
                    self.df.loc[ind,'AskPrice'+str(1+i)]=self.df.loc[ind,'AskPrice'+str(i+1+needfix)]
                    self.df.loc[ind,'AskVolume'+str(1+i)]=self.df.loc[ind,'AskVolume'+str(i+1+needfix)]
                for i in range(needfix):#删除不需要价位
                    self.df.loc[ind,'AskPrice'+str(self.price_level-i)]=0
                    self.df.loc[ind,'AskVolume'+str(self.price_level-i)]=0
#        bid<min 舍去这个bid以及更低的bid
#        bid in [min,max) 不处理
#        bid in [max,++)
#            将这个之前的bidsize都加到max的价格上
#                   由于顺序问题  取前面的操作无法实现只能通过这种方式进行
#                   下一个存在？
#                    存在
#                        大于等于high？
#                            量加到下一档  价格删除
#                        小于high
#                            本档价格变成high 量不变
#                    不存在
#                        本档价格变成high 量不变
#
#            不存在价格为max的bid 将这个及之后的价格都加总 放到新建价格为max的bid的价格上
    @betimer
    def volume_adj(self):
        self.uni_f()
        f=lambda x:x
        volume=[f(x) for x in self.df.index]
        self.df['volume']=volume
    def va(self,tm):
        ori_dt=tm
        post_tm=tm
        return tm.volume*self.f_dict[0](post_tm)/self.f_dict[ori_dt](tm)
        pass
    def uni_f(self):
        self.f_dict=dict()
        for dt in self.dates:
            f=lambda x:x
            self.f_dict[dt]=f
        self.f_dict[0]=f


        pass
        #n=一共几天
        #对于每天 and 这几天合起来
            #开盘处理
                #对于符合条件的bar
                #这种条件有三个 第一分钟 最后一分钟 全部时长
                #计算这个参数 也就是平均的量 sum(bar total volume)/sum(bar total number)
                    #计算方式
                #对于全部时长 算好后需要乘以之后的bar数 开盘(60/3)*(10:00-9:30) 也就是20*30
                #这样我们就得到了f(11) f(20*(30-1)+11) F(20*30) F为f的原函数
                #通过f f F 我们可以解出f的表达式 f=axx+bx+c 前面就是利用三个点来确定一条二次曲线
                #这样我们就得到了每天的开盘基准
            #盘中处理
                #对于所有盘中数据取平均值
            #收盘处理
                #仅有深交所处理 同开盘处理
        #对于全部这几天的计算结果让我们有了一个基准

        #获取特定时间段的bar切片
        #=xx[(xx.index>pd.Timestamp("20180601 08:59:59"))*(xx.index<pd.Timestamp("20180601 09:59:59"))]

        #对于每个bar的数据
            #找到其对应的原始数据的位置
            #计算出其对于当天的基准偏离比例
            #在将这个比例乘到全部天的基准上
            #这就得到了新的量的数据






        pass
    @betimer
    def auction_adj(self):
        #价格
            #原始的今开盘集合竞价*(经过价格调整的昨收盘/原始的昨收盘)
        #数量
            #就是第一天的集合竞价数量*(1+0.2*(rand-0.5))
            #微幅改变数量以免透露是哪天的信息

        #收盘集合竞价数据同样处理 昨收盘变成14:27的收盘数据
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
c.set_today("20180601")
c.set_ctr("600000")
c.set_date_range([20180102,20180103])
c.set_price_level(5)
c.load_histroy()
c.time_grep()
c.time_select()
c.conbine_bar()
c.timestamp_adj()
c.df.to_csv("before_hl.csv")
c.hl_limit_adj()
c.df.to_csv("after_hl.csv")
#x=c.clean_df
xx=c.df
#tmp=x[['BidPrice1','AskPrice1','BidVolume1','AskVolume1','TradingDay','UpdateTime','UpdateMillisec']]




#
#plt.plot(list(filter(lambda x:x>0,c.clean_df['BidPrice1'])))
#plt.savefig('rawbid.png', dpi=100)
#plt.close()
#
#
#plt.plot(list(c.df['BidPrice1']))
#plt.savefig('cleanbid.png', dpi=100)
#plt.close()
'''
生成nbbo
空值就是,,

存在的问题
明显异于其他档位的size是个很奇怪的存在  本来是在一个价位的 fake后会在不同价位跳动
'''