# -*- coding: utf-8 -*-
"""
Created on Sat Jul 21 10:20:38 2018

@author: admin
"""
#import pandas as pd
'''
#
#a=pd.read_csv("6all.csv",parse_dates=True,encoding="GBK")
#
p=["Price",'Volume']
q=["Bid",'Ask']
#x=[x+"Price" for x in y];print(x)
#y=zip(y,z);x=[x[0]+x[1] for x in y];print(x)
#a=reduce(add,[[i+j for i in p] for j in q])
x=reduce(add,[[str(t)+str(s+1) for t in reduce(add,[[i+j for i in ["Bid",'Ask']] for j in ["Price",'Volume']])] for s in range(5)]);
print(x)
'''



'''
from datetime import datetime
btime=datetime.now()
import pandas as pd
import gzip
f=gzip.open("C:\code\hx_data\stock_tick.csv.gz")
etime=datetime.now()-btime;print(etime);btime=datetime.now()
xx=pd.read_csv(f,parse_dates=True,encoding="GBK")
etime=datetime.now()-btime;print(etime);btime=datetime.now()
ind=list(xx['日期']+" "+xx['时间'])
etime=datetime.now()-btime;print(etime);btime=datetime.now()
ind2=[pd.Timestamp(x) for x in ind] #40s
etime=datetime.now()-btime;print(etime);btime=datetime.now()
xx.index=ind2 #46s
etime=datetime.now()-btime;print(etime);btime=datetime.now()


xx.to_csv("2.csv")#0:11:25.245717
etime=datetime.now()-btime;print(etime);btime=datetime.now()
fz=gzip.open('2.csv.gz', 'wt');xx.to_csv(fz)
etime=datetime.now()-btime;print(etime);btime=datetime.now()
f.close()
fz.close()
#gzip 1.csv  1:24
#sort_index
'''

'''
令总体函数为 f(i)=x i为第几个tick x为相应的成交量
先取第一分钟 p 最后一分钟 q 全部分钟 r
tick算的话 3秒一个  那也就是 f(11)=p/21 f((30-1)*20+11)=q/21 积分f 0 到20*30+1 ==r

f(i)=a*i*i+b*i+c
F(i)=a*i*i*i/3 + b*i*i/2 +c*i

'''



'''
import matplotlib.pyplot as plt
from sympy import *
from sympy.abc import a,b,c
p1=11
p2=20*(30-1)+11
p3=20*30+1
p=100/20
q=20/20
r=1500
[a1,b1,c1]=solve([a*p1*p1+b*p1+c-p,a*p2*p2+b*p2+c-q,a*p3*p3*p3/3+b*p3*p3/2+c*p3-r],[a,b,c]).values()
f=lambda x:a1*x*x+b1*x+c1
[a2,b2,c2]=solve([a*p1*p1+b*p1+c-p,a*p2*p2+b*p2+c-q,a*p3*p3*p3/3+b*p3*p3/2+c*p3-r],[a,b,c]).values()
f=lambda x:a2*x*x+b2*x+c2
plt.plot([f(i) for i in range(600)])
'''

import json
json.load("C:\code\project\dubi\para.json")


