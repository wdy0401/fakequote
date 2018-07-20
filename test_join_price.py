# -*- coding: utf-8 -*-
"""
Created on Fri Jul 20 14:43:40 2018

@author: admin
"""
import pandas as pd
tail_tag="_next"
columns=['Bid']
y=x.loc[x.index[0:20],['BidPrice1','AskPrice1']]
y0=x.loc[x.index[0:20],['BidPrice1']]
y0.columns=columns
y1=y0[1:]
y1.index=y0.index[0:-1]
y1.columns=[str(x)+tail_tag for x in columns]
y2=pd.concat([y0,y1],axis=1)
y3=y2.iloc[[1,3,5,6,7,9,15,18]]

#按照保证bar之间价格差的方式生成新序列
#这会存在bid可能大于ask的状况  处理方式是以bid为基准  修复之
ph=dict()
lastp=0
pdif=0

ph['Bid']=list()
for i,j in enumerate(y3.index):
    if i==0:
        ph['Bid'].append(y3.loc[j,'Bid'])
    else:
        ph['Bid'].append(lastp+pdif)
    pdif=y3.loc[j,'Bid'+tail_tag]-y3.loc[j,'Bid']
    lastp=ph['Bid'][-1]
ph['Bid']=[round(x,2) for x in ph['Bid']]

ph["Ask"]=list()
for i in range(len(ph['Bid'])):
    ph["Ask"].append(round(ph["Bid"][i]+y.iloc[i,1]-y.iloc[i,0],2))
    
z=pd.DataFrame(ph,index=y3.index)
#以bid为标准  if ask<bid ask=bid+preask-prebid


