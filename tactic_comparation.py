#!/usr/bin/python3

#输入为para_cal.py的输出
#无标题的csv格式 第一列为策略名 其余列请参照paralist给出
import pandas as pd
import math

import warnings
warnings.filterwarnings("ignore")

paralist=["yret","eyret","yshp","yic","alpha","beta","maxdrop","yvol","downvol","sortino"]
d=pd.read_csv("tactic_para.csv",header=None,index_col=0,names=paralist)


d['rank']=0 
duni=d[d['yret']>=0]
dnuni=d[d['yret']<0]
if len(duni>0):   
    for ind in ["yret","yshp","maxdrop"]:
        high=duni[ind].max()
        low=duni[ind].min()
        hlrg=high-low
        if hlrg==0:
            duni[ind]=duni[ind].apply(lambda x:1)
        else:
            duni[ind]=duni[ind].apply(lambda x:(x-low)/hlrg)
            if ind=='yshp':
                duni[ind]=duni[ind].apply(lambda x:(math.exp(x)-1)/(math.e-1))
            if ind=='maxdrop':
                duni[ind]=duni[ind].apply(lambda x:(math.e-math.exp(x))/(math.e-1))
        duni['rank']=duni['rank']+duni[ind]
if len(dnuni>0):   
   dnuni['rank']=dnuni['yret']

def print_rank(dpara):
    if len(dpara>0):
        order=dict(zip(dpara.index,dpara['rank']))
        for rank_value in sorted(order.values(),reverse=True):
            for i in order.keys():#这个循环解决了重复rank_value的问题
                if order[i]==rank_value:
                    print(print_rank.ranking,i,round(order[i],4))
                    print_rank.ranking=print_rank.ranking+1
print_rank.ranking=1
print_rank(duni)
print_rank(dnuni)


'''
	同类策略排名步骤
	排除收益为负的策略
	将各个指标进行归一化处理
	收益率分值不变
	夏普比率按照公式(e^x-1)⁄(e-1)进行处理
	最大回撤按公式 (e-e^x)⁄(e-1)进行处理
	将收益率，夏普，最大回撤分数相加并排名得到同类策略排名结果
	其他指标作为定性比较参考依据
	
    尚未得到策略类别信息 下面方法暂无法实现
    非同类策略排名步骤
	将策略进行同类排名
	选出每类排名前三的策略
	将选出的策略按夏普比率进行排名得到非同类策略排名结果
	其他指标所谓定性比较参考依据
'''