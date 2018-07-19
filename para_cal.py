#!/usr/bin/python3

import numpy as np
import math
import os,sys 
from functools import reduce
YTD=252#每年交易日数量

'''ind_cal函数接受一个净值序列 一个参考序列 返回收益风险指标
i.	收类指标
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

传入为单位净值或净值序列
传入序列数据类型为list或np.array
nv为净值序列 bm为参考序列：如hs300 
nv与bm需等长
'''
def check_quote_error(nv,bm):
    re=""
    if(len(nv)!=len(bm)):
        re=re+" Length Error\t"
    if(nv[0]==0 or bm[0]==0):
        re=re+" First Netvalue Error\t"
    return re
def ind_cal(nv,bm,name):
    error=check_quote_error(nv,bm)
    if error:
        print(error)
        return""
    #转换成单位净值
    [nv,bm]=[np.array(x)/x[0] for x in [nv,bm]]
    #收益率序列
    [retnv,retbm]=[np.array([(x[i+1]-x[i])/x[i] for i in range(len(x)-1)]) for x in [nv,bm]]
    #最终净值
    [lastnv,lastbm]=[nv[-1],bm[-1]]
    #交易天数
    length=nv.size
    
    yret=(lastnv-1)*YTD/length
    eyret=(lastnv-lastbm)*YTD/length
    yvol=retnv.std()*(math.sqrt(YTD/length))
    yshp=0
    if yret==0 and yvol==0:
        yshp=0
    elif yvol==0:
        yshp=np.inf
    yic=0
    if reduce(lambda x,y:x and y,retnv==retbm):
        if eyret==0:
            yic=0
        else:
            yic=np.inf
    else:
        yic=(eyret)/((retnv-retbm).std()*(math.sqrt(YTD/length)))
    maxdrop=max([(nv[0:x+1].max()-nv[x])/nv[0:x+1].max() for x in range(len(nv))])
    beta=np.corrcoef(retnv,retbm)[0,1]
    alpha=(lastnv-1-(lastbm-1)*beta)*YTD/length
    
    downpart=np.array(list(filter(lambda x: x<0,retnv.tolist())))
    downvol=0
    sortino=0
    if len(downpart)>0:
        downvol=downpart.std()*(math.sqrt(YTD/len(downpart)))
        sortino=yret/downvol
    rlist=[yret,eyret,yshp,yic,alpha,beta,maxdrop,yvol,downvol,sortino]
    plist=[str(round(x,4)) for x in rlist]
    print_list=",".join([name]+plist)
    return print_list

def load_net(fname):
    with open(fname) as f:
        return [float(str.strip(x)) for x in f.readlines()]

usedir="./data"
with open("tactic_para.csv","w") as f:
    dirs=os.listdir(usedir)
    for fn in dirs:
        sys.stderr.write(fn+"\n")
        if fn[-3:]=="csv":     
            nv=load_net(usedir+"/"+fn);nv[-1]=nv[-1]+1e-10
            fakebm=[1+0.0001*i for i in range(len(nv))];fakebm[-1]=fakebm[-1]+1e-10
            f.write(ind_cal(nv,fakebm,os.path.split(fn)[1][0:-4])+"\n")


    
    