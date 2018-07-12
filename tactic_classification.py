#!/usr/bin/python3

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