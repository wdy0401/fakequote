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

def print_rank(dpara,f):
    if len(dpara>0):
        order=dict(zip(dpara.index,dpara['rank']))
        for rank_value in set(sorted(order.values(),reverse=True)):
            for i in order.keys():#这个循环解决了重复rank_value的问题
                if order[i]==rank_value:
                    f.write(",".join([str(x) for x in [print_rank.ranking,i,round(order[i],4),*list(d.loc[i])]])+"\n")
                    print_rank.ranking=print_rank.ranking+1
with open("tactic_rank.csv","w") as f: 
    print_rank.ranking=1
    print_rank(duni,f)
    print_rank(dnuni,f)

