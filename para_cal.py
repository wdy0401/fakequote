#!/usr/bin/python3

import numpy as np
import math
import sys
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
    yshp=yret/yvol
    yic=(eyret)/((retnv-retbm).std()*(math.sqrt(YTD/length)))
    maxdrop=max([(nv[0:x+1].max()-nv[x])/nv[0:x+1].max() for x in range(len(nv))])
    beta=np.corrcoef(retnv,retbm)[0,1]
    alpha=(lastnv-1-(lastbm-1)*beta)*YTD/length
    
    downpart=np.array(list(filter(lambda x: x<0,retnv.tolist())))
    downvol=downpart.std()*(math.sqrt(YTD/len(downpart)))
    sortino=yret/downvol
    rlist=[yret,eyret,yshp,yic,alpha,beta,maxdrop,yvol,downvol,sortino]
    plist=[str(round(x,4)) for x in rlist]
    sys.stderr.write("策略名,年化收益率,超额收益率,夏普比率,信息比率,阿尔法,贝塔,最大回撤,年化波动率,下行波动率,索提诺比率")
    sys.stderr.write(",".join([name]+plist))
    print(",".join([name]+plist))
    return rlist

nv=np.array([1,1.33518481,0.5947847,1.56663256,1.07746506,0.99541804,1.09275599,1.23980119,1.08549716,1.17878604,1.43788036,1.84143297,1.71776313,1.64087145,1.84838018,1.87778502,2.12587365,1.8996966,2.35480062,2.35346487])
bm=np.array([1,1.04650794,0.71964821,1.21264349,1.27265859,1.13142881,1.16854388,1.09086115,1.29109976,1.16364775,1.53104984,1.77451284,1.56222544,1.63383812,1.4862519,1.95264773,1.81769526,1.85748236,2.11899229,1.99498051])
ind_cal(nv,bm,"Tactic1")
