# -*- coding: utf-8 -*-
"""
Created on Tue Jul 10 14:15:46 2018

@author: ccc
"""

'''
先算净值
    daliy sum(position*closeprice)+cash
再算相关指标

i.	收益类指标
    1.	年化收益率
    2.	超额收益率
    3.	夏普比率
    4.	信息比率
    5.	阿尔法
    6.	贝塔
ii.	风险类指标
    1.	最大回撤
    2.	年化波动率
    3.	索提诺比率
    4.	下行波动率
'''

import numpy as np
import math
from functools import reduce

    
nv=0.1*np.array(range(20))+1+np.random.rand(20)
bm=nv-0.55+np.random.rand(20)
#print(para(nv,'xxx'))

#传入为净值序列 或者实际价值序列
#净值序列
[nv,bm]=[np.array(x)/x[0] for x in [nv,bm]]
#收益率序列
[retnv,retbm]=[np.array([[(x[i+1]-x[i])/x[i] for i in range(len(x)-1)]]) for x in [nv,bm]]
#最终净值
[lastnv,lastbm]=[nv[-1],bm[-1]]

length=nv.size
std=nv.std()/(math.sqrt(length/252))

yret=(lastnv-1)*252/length
eyret=(lastnv-lastbm)*252/length
yshp=(yret)/(retnv.std()/(math.sqrt(length/252)))
yic=(eyret)/((retnv-retbm).std()/(math.sqrt(length/252)))
maxdrop=max([(nv[0:x+1].max()-nv[x])/nv[0:x+1].max() for x in range(len(nv))])
beta=np.corrcoef(retnv,retbm)[0,1]
alpha=lastnv-1-(lastbm-1)*beta

yvol=retnv.std()
downpart=np.array(list(filter(lambda x: x<0,retnv.tolist()[0])))
downvol=downpart.std()/(math.sqrt(len(downpart)/252))
sortino=yret/downvol
print("年化收益率,超额收益率,夏普比率,信息比率,阿尔法,贝塔,最大回撤,年化波动率,下行波动率,索提诺比率")
print(yret,eyret,yshp,yic,alpha,beta,maxdrop,yvol,downvol,sortino)
'''
i.	收益类指标
    1.	年化收益率
    2.	超额收益率
    3.	夏普比率
    4.	信息比率
    5.	阿尔法
    6.	贝塔
ii.	风险类指标
    1.	最大回撤
    2.	年化波动率
    3.	索提诺比率
    4.	下行波动率
'''

'''
超额收益率  收益-基准收益 eg.hs300
信息比率 std(收益-基准收益)
alpha 收益-beta*基准收益
beta  corr(收益,基准收益)
下行波动率 std(when return<0)
索提诺比率  收益/下行波动率

'''

'''
分类指标逐个处理
可以区分acd

a)	按交易品种分类
    i.	权益型策略
        1.	股票投资占比大于80%
    ii.	固收型策略
        1.	现金,债券投资大于80%
    iii.	衍生品型策略
        1.	期货,期权投资大于80%
    iv.	混合型策略
        1.	未达到前三类产品标准的
b)	按信号来源分类
    i.	主观交易策略
        1.	人工下单
    ii.	程序化交易策略
        1.	人工下单或程序化下单
c)	按持仓长短分类
    i.	长线策略
        1.	平均持仓时间大于25个交易日
    ii.	中线策略
        1.	平均持仓时间大于5个工作日
   iii.	短线策略
        1.	平均持仓时间小于5个工作日
d)	按是否对冲分类
    i.	市场中性策略
        1.	Abs(多-空)/Max（多,空）<1/3
    ii.	单边策略
        1.	非市场中性策略
'''
#winratio=0
#dailypnl=[nv[i]-nv[i-1] for i in range(1,len(nv))]
#win=reduce(lambda x, y: x+y, filter(lambda x: x>0,dailypnl),0)
#loss=reduce(lambda x, y: x+y, filter(lambda x: x<0,dailypnl),0)
#winratio=abs(win)/(abs(win)+abs(loss))