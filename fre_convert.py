# -*- coding: utf-8 -*-
"""
Created on Wed Jul 11 09:36:55 2018

@author: admin
"""
"""
将历史成交数据变频成分钟K线数据
根据需求修改 日期 路径 文件名
保存了9：25集合成交的数据
"""

import pandas as pd

file="./data/600000/2018/7/600000_2018-07-02.csv"
a=pd.read_csv(file,index_col=0,parse_dates=True)
b=[pd.Timestamp("2018-07-02 "+a['time'][i]) for i in range(len(a['time']))]
a.index=b
price=a.price.resample('1Min').ohlc()
volume=pd.DataFrame(a.volume.resample('1Min').sum(),index=price.index,columns=['volume'])
amount=pd.DataFrame(a.amount.resample('1Min').sum(),index=price.index,columns=['amount'])
re=pd.concat([price,volume,amount],sort=True,axis=1)
re=re.dropna(how='any')
re=re.drop(index=pd.Timestamp("2018-07-02 "+"09:29:00"))
#需更改为保存的文件名
fn="600000_2018-07-02.csv"
re.to_csv("0.csv")
