# -*- coding: utf-8 -*-
"""
Created on Tue Jul 10 09:42:05 2018

@author: admin
"""

#script utils
import warnings
warnings.filterwarnings("ignore")
from functools import reduce,wraps
import os,sys,types,pathlib

#data utils
import pandas as pd
import numpy as np
import random
from datetime import datetime
import matplotlib.pyplot as plt
import sqlite3
import gzip

#solve function
from sympy import *
from sympy.abc import a,b,c

#day info transfer
import json

win=True
import platform
if 'windows' not in platform.platform().lower():
    win=False

prterr=lambda x : sys.stderr.write(x)


def betimer(func):
    @wraps(func)
    def wrapper(*args, **kw):
#        btime=datetime.now()
        ret=func(*args, **kw)
#        dift=datetime.now()-btime
#        print('%s %s' % (func.__name__ , dift))
        return ret
    return wrapper
def date_map(odts,ndts,random_seed=None):
    random.seed(random_seed)
    num_map=dict()
    olen=len(odts)
    nlen=len(ndts)
    if (olen/nlen)<2:
        sys.exit(f"ERROR:date_map not enough dates\n")
    maxsize=2+int(olen/nlen)
    for i in range(nlen):
        num_map[i]=2
    remain=olen-nlen*2
    i=0
    while(i<remain):
        j=random.randrange(nlen)
        if num_map[j]<maxsize:
            i+=1
            num_map[j]+=1
    dt_map=dict()
    j=0
    for i in range(nlen):
        dt_map[ndts[i]]=odts[j:j+num_map[i]]
        j+=num_map[i]
    return dt_map
class stock(object):
    def __init__(self):
        self.t_delta=pd.Timedelta('0 days 00:00:03')
        self.json=dict()
    def pre(self,fn):
        if type(fn)==type(str()):
            with open(fn) as f:
                self.his=json.load(f)
        elif type(fn)==type(dict()):
            self.his=fn
        else:
            return
        for k,v in self.his.items():
            if hasattr(self,k) and type(getattr(self,k))==types.MethodType:
                prterr(f"ERROR:load_his {k}\n")
            else:
                setattr(self,k,v)
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
            fname=self.gen_old_file_name(dt)
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
            fname=self.gen_old_file_name(dt)
            if fname[-2:]=='gz':
                with gzip.open(fname,mode='rt') as f:
                    nms=["SecurityID","TradingDay","UpdateTime","PreClosePrice","OpenPrice","HighestPrice","LowestPrice","LastPrice","Volume","x1","x2","BidPrice1","BidVolume1","BidPrice2","BidVolume2","BidPrice3","BidVolume3","BidPrice4","BidVolume4","BidPrice5","BidVolume5","AskPrice1","AskVolume1","AskPrice2","AskVolume2","AskPrice3","AskVolume3","AskPrice4","AskVolume4","AskPrice5","AskVolume5","BidPrice6","BidVolume6","BidPrice7","BidVolume7","BidPrice8","BidVolume8","BidPrice9","BidVolume9","BidPrice10","BidVolume10","AskPrice6","AskVolume6","AskPrice7","AskVolume7","AskPrice8","AskVolume8","AskPrice9","AskVolume9","AskPrice10","AskVolume10","x3","x4","x5","x6"]
                    a=pd.read_csv(f,parse_dates=True,names=nms)
                    a.index=[pd.Timestamp(x) for x in a['TradingDay']+" "+a['UpdateTime']]

            else:
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
        i='Volume'
        last_dt=0
        last_v=0
        lst=list()
        for j in self.clean_df.index:
            dt=int(self.clean_df.loc[j,"grep"].strftime("%Y%m%d"))
            v=self.clean_df.loc[j,i]
            if dt==last_dt:
                lst.append(v-last_v)
            else:
                lst.append(v)
            last_dt=dt
            last_v=v
        self.clean_df['Volume_dif']=lst
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
        self.df=self.clean_df.copy()
        tail_tag="_next"
        columns=['BidPrice1']
        add=lambda x,y:x+y
        self.item_list=reduce(add,[[str(t)+str(s+1) for t in reduce(add,[[i+j for i in ["Bid",'Ask']] for j in ["Price",'Volume']])] for s in range(self.price_level)]);
        self.item_list.extend(["Volume_dif","LastPrice","grep"])
        item_list=self.item_list
        #item_dict=dict(enumerate(item_list))
        #item_dict_r= {v:k for k,v in item_dict.items()}
        y=self.df.loc[:,item_list]
        y0=self.df.loc[:,['BidPrice1']]
        y0.columns=columns
        y1=y0[1:]
        y1.index=y0.index[0:-1]
        y1.columns=[str(x)+tail_tag for x in columns]
        y2=pd.concat([y0,y1],axis=1)
        y3=y2.iloc[self.sortlist]
#        self.y=y
#        self.y0=y0
#        self.y1=y1
#        self.y2=y2
#        self.y3=y3

        ph=dict()
        lastp=0
        pdif=0

        ph['BidPrice1']=list()
        for i,j in enumerate(y3.index):
            if i==0:
                if hasattr(self, 'pre_close'):
                    p=y3.loc[j,'BidPrice1']*self.pre_close/self.pre_close_old#转换为可比价格
                    p=round(p,2)
                    ph['BidPrice1'].append(p)
                    print(self.ctr,self.today,"OPEN 1",p,y3.loc[j,'BidPrice1'],self.pre_close,self.pre_close_old)
                else:
                    ph['BidPrice1'].append(y3.loc[j,'BidPrice1'])
                    print(self.ctr,self.today,"OPEN 2",y3.loc[j,'BidPrice1'])
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
                if "Price" in price:
                    for i in range(len(ph['BidPrice1'])):
                        j=y3.index[i]
                        ph[price].append(round(ph["BidPrice1"][i]+y.loc[j,price]-y.loc[j,'BidPrice1'],2))
#                        ph[price].append(round(ph["BidPrice1"][i]+y.iloc[i,item_dict_r[price]]-y.iloc[i,0],2))
                else:
                    for i in range(len(ph['BidPrice1'])):
                        j=y3.index[i]
                        ph[price].append(y.loc[j,price])
        self.ph=ph
        self.df=pd.DataFrame(ph,index=y3.index)
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
            print(self.ctr,self.today,pc,1)
        else:
            tmp=self.df.iloc[0,:]
            pc=round((tmp['BidPrice1']*tmp['BidVolume1']+\
                     tmp['AskPrice1']*tmp['AskVolume1'])/(\
                        tmp['BidVolume1']+tmp['AskVolume1']),2)
            #pc=round(((tmp['BidPrice1']+tmp['AskPrice1'])/2),2)
            print(self.ctr,self.today,pc,2)
        self.high_limit=round(pc*1.1,2)
        #self.high_limit=12.7
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

            #Last price
            lp=self.df.loc[ind,'LastPrice']
            if lp>self.high_limit:#大于涨停板的卖价 全部删除
                self.df.loc[ind,'LastPrice']=self.high_limit
            elif lp<self.low_limit:
                self.df.loc[ind,'LastPrice']=self.low_limit
    @betimer
    def volume_adj(self):
        self.uni_f()
        volume=[int(self.va(x)) for x in self.df.index]
        self.df['Volume_dif']=volume
    def va(self,tm):#这个tm是post tm
        barpost=self.tm_barnum(tm)
        barpre=self.tm_barnum(self.df.loc[tm,'grep'])
        ori_dt=int(self.df.loc[tm,'grep'].strftime("%Y%m%d"))
        re=self.df.loc[tm,"Volume_dif"]*self.f_dict[0](barpost)/self.f_dict[ori_dt](barpre)
#        if re<10000:
#            print(tm,barpost,barpre,ori_dt,re)
#            print(self.df.loc[tm,"Volume_dif"])
#            print(self.f_dict[0](barpost))
#            print(self.f_dict[ori_dt](barpre))
        return re
    def uni_f(self):
        self.f_dict=dict()
        bar_ind={"open":[
                        11,
                        20*(30-1)+11,
                        20*30+1],
                'close_1':[
                        20*60*4-20*15+11,
                        20*60*4-20*15 +20*(15-1)+11,
                        20*15+1],
                'close_2':[
                        20*60*4-20*15+11,
                        20*60*4-20*15 +20*(12-1)+11,
                        20*12+1]
                }
        x_total=[0 for i in range(8)]
        for dt in self.dates:
            #open
            [x1,x2,x3]=bar_ind["open"]
            idx_first=(self.clean_df['grep']>=pd.Timestamp(str(dt)+" 09:30:00" ))&(self.clean_df['grep']<=pd.Timestamp(str(dt)+" 09:31:00" ))
            idx_last=(self.clean_df['grep']>=pd.Timestamp(str(dt)+" 09:59:00" ))&(self.clean_df['grep']<=pd.Timestamp(str(dt)+" 10:00:00" ))
            idx_all=(self.clean_df['grep']>=pd.Timestamp(str(dt)+" 09:30:00" ))&(self.clean_df['grep']<=pd.Timestamp(str(dt)+" 10:00:00" ))

            p=self.clean_df[idx_first]['Volume_dif'].sum()/20;x_total[1]+=p
            q=self.clean_df[idx_last]['Volume_dif'].sum()/20;x_total[2]+=q
            r=self.clean_df[idx_all]['Volume_dif'].sum();x_total[3]+=r
            #输入是第几根bar  输出是对应的标准量
            [a1,a2,a3]=solve([a*x1*x1+b*x1+c-p,a*x2*x2+b*x2+c-q,a*x3*x3*x3/3+b*x3*x3/2+c*x3-r],[a,b,c]).values()
            #先确定是第几个bar 然后 根据公式得到标准量
            o_mean=q/x3
            #print([dt,'open',p,q,r,a1,a2,a3])

            #close
            if self.mkt==1:
                [x1,x2,x3]=bar_ind["close_1"]
                idx_first=(self.clean_df['grep']>=pd.Timestamp(str(dt)+" 14:45:00" ))&(self.clean_df['grep']<=pd.Timestamp(str(dt)+" 14:46:00" ))
                idx_last=(self.clean_df['grep']>=pd.Timestamp(str(dt)+" 14:59:00" ))&(self.clean_df['grep']<=pd.Timestamp(str(dt)+" 15:00:00" ))
                idx_all=(self.clean_df['grep']>=pd.Timestamp(str(dt)+" 14:45:00" ))&(self.clean_df['grep']<=pd.Timestamp(str(dt)+" 15:00:00" ))
            if self.mkt==2:
                [x1,x2,x3]=bar_ind["close_2"]
                idx_first=(self.clean_df['grep']>=pd.Timestamp(str(dt)+" 14:45:00" ))&(self.clean_df['grep']<=pd.Timestamp(str(dt)+" 14:46:00" ))
                idx_last=(self.clean_df['grep']>=pd.Timestamp(str(dt)+" 14:56:00" ))&(self.clean_df['grep']<=pd.Timestamp(str(dt)+" 15:00:00" ))
                idx_all=(self.clean_df['grep']>=pd.Timestamp(str(dt)+" 14:45:00" ))&(self.clean_df['grep']<=pd.Timestamp(str(dt)+" 15:00:00" ))

            p=self.clean_df[idx_first]['Volume_dif'].sum()/20;x_total[4]+=p
            q=self.clean_df[idx_last]['Volume_dif'].sum()/20;x_total[5]+=q
            r=self.clean_df[idx_all]['Volume_dif'].sum();x_total[6]+=r
            [b1,b2,b3]=solve([a*x1*x1+b*x1+c-p,a*x2*x2+b*x2+c-q,a*x3*x3*x3/3+b*x3*x3/2+c*x3-r],[a,b,c]).values()

            idx_all=(self.clean_df['grep']>=pd.Timestamp(str(dt)+" 10:00:00" ))&(self.clean_df['grep']<=pd.Timestamp(str(dt)+" 14:45:00" ))
            cc=self.clean_df[idx_all]['Volume_dif'].sum()/((4*60-15-30)*20);x_total[7]+=cc
            c_mean=q/x3
            self.f_dict[dt]=lambda x: self.vf(a1,a2,a3,b1,b2,b3,cc,o_mean,c_mean,x)
            #print([dt,'close',p,q,r,b1,b2,b3,cc])

        x_total=[x_total[i]/len(self.dates) for i in range(len(x_total))]

        [p,q,r]=[x_total[i] for i in range(1,4)]
        [x1,x2,x3]=bar_ind["open"]
        [a1,a2,a3]=solve([a*x1*x1+b*x1+c-p,a*x2*x2+b*x2+c-q,a*x3*x3*x3/3+b*x3*x3/2+c*x3-r],[a,b,c]).values()
        o_mean=q/x3

        [p,q,r]=[x_total[i] for i in range(4,7)]
        if self.mkt==1:
            [x1,x2,x3]=bar_ind["close_1"]
        if self.mkt==2:
            [x1,x2,x3]=bar_ind["close_2"]
        [b1,b2,b3]=solve([a*x1*x1+b*x1+c-p,a*x2*x2+b*x2+c-q,a*x3*x3*x3/3+b*x3*x3/2+c*x3-r],[a,b,c]).values()
        cc=x_total[7]
        c_mean=q/3
        self.f_dict[0]=lambda x: self.vf(a1,a2,a3,b1,b2,b3,cc,o_mean,c_mean,x)
        #print([dt,'total',a1,a2,a3,b1,b2,b3,cc])

    def tm_barnum(self,tm):
        re=int((tm-pd.Timestamp(tm.date())- pd.Timedelta('0 days 09:30:00'))/self.t_delta)
        if re>20*60*2:#早盘2小时
            re=re-20*60*1.5#午休1.5小时
        return int(re)
    def vf(self,a1,a2,a3,b1,b2,b3,c,o_mean,c_mean,x):#对于开盘收盘 因为可能存在2次曲线到达负值的情形 所以设定了最低限制 mean/10
        if x<=20*30+1:#开盘
            re=a1*x*x+a2*x+a3
            if re>o_mean/10:
                return re
            else:
                return o_mean/10
        elif x>20*60*4-20*15:#收盘
            re=b1*x*x+b2*x+b3
            if re>c_mean/10:
                return re
            else:
                return c_mean/10
        else:#盘中
            return c
    @betimer
    def auction_adj(self):
        #价格
            #(经过价格调整的昨收盘*(原始的今开盘集合竞价/原始的昨收盘)
        #数量
            #就是第一天的集合竞价数量*(1+0.2*(rand-0.5))
            #微幅改变数量以免透露是哪天的信息

        #收盘集合竞价数据同样处理 昨收盘变成14:57的收盘数据
        pass
    def gen_old_file_name(self,dt):
        #return f"./data/md/{dt}/{self.ctr}_{self.mkt}.bak.csv"
        if win:
            return f"./data/old/{self.ctr}/{dt}.txt.gz"
        else:
            year=str(dt)[0:4]
            mon=str(dt)[4:6]
            day=str(dt)[6:]
            if self.mkt==1:
                return f"../THS/tick/stock_tick/{year}/{mon}/{day}/txt/SH{self.ctr}.txt.gz"
            else:
                return f"../THS/tick/stock_tick/{year}/{mon}/{day}/txt/SZ{self.ctr}.txt.gz"
    def trading_time_grep(self,x):
        if ((x.hour==9 and x.minute>29) \
            or (x.hour==10) \
            or (x.hour==11 and x.minute<31) \
            or (x.hour==13) \
            or (self.mkt==1 and x.hour==14) \
            or (self.mkt==2 and x.hour==14 and x.minute<57) \

            ):#open close auction(x.hour==9 and x.minute==25)  (x.hour==15 and x.minute==0)

            return x
        else:
            return 0
    def fix_volume(self):
        tmp=self.df.copy()
        tmp.pop('grep')
        vo=tmp['Volume_dif']
        lastv=0
        v=list()
        for i in range(len(vo)):
            lastv+=vo[i]
            v.append(lastv)
        tmp['Volume']=v
        tmp.pop("Volume_dif")
        self.csv=tmp
    def to_csv(self):
        self.fix_volume()
        if win:
            self.csv.to_csv(f"./data/new/{self.today}/{self.ctr}.csv",line_terminator="\n")
        else:
            self.csv.to_csv(f"../THS/fakequote/{self.today}/{self.ctr}.csv",line_terminator="\n")
    def post(self):
        last_tm=self.csv.index[-1]
        last_old_tm=self.df['grep'][-1]
        self.json['LastPrice']=self.csv.loc[last_tm,'LastPrice']
        self.json['old_LastPrice']=self.clean_df.loc[last_old_tm,'LastPrice']
#        with open(f"./{self.today}.json","w") as f:
#            json.dump(self.json,f)
        dts=tuple([self.today,self.ctr,self.dates[0],self.dates[-1],self.json['LastPrice'],self.json['old_LastPrice']])

        fn=f"./info/{self.ctr}.db"
        if not os.path.exists(fn):
            self.conn=sqlite3.connect(fn)
            self.cursor=self.conn.cursor()
            self.cursor.execute('CREATE TABLE daily_price (\
                                    date   INT,\
                                    ctr    STRING,\
                                    bdate  INT,\
                                    edate  INT,\
                                    close  DOUBLE,\
                                    old_close DOUBLE,\
                                    primary key (date,ctr,bdate))')
            self.conn.commit()
        else:
            self.conn=sqlite3.connect(fn)
            self.cursor=self.conn.cursor()
        self.cursor.execute('insert or replace into daily_price (date,ctr,bdate,edate,close,old_close) values (?,?,?,?,?,?)', dts)
        self.conn.commit()
        self.conn.close()
#zz=stock()
#zz.set_today("20180601")
#zz.pre("./a.json")
#zz.set_ctr("600000")
#zz.set_date_range([20180102,20180103])
#zz.set_price_level(5)
#zz.load_histroy()
#zz.time_grep()
#zz.time_select()
#
#zz.conbine_bar()
#zz.timestamp_adj()
#zz.hl_limit_adj()
#zz.volume_adj()
#zz.to_csv()
#zz.post()
#xx=zz.df
#xx.to_csv('df.csv')

