# -*- coding: utf-8 -*-
"""
Created on Tue Jul 10 09:42:05 2018

@author: admin
"""

'''
faketime   oritime    method
9-10       9-11       压缩
9-10       9-9.5      拉伸
9-10       10-11      删除
'''
from datetime import datetime
import pandas as pd

#b=pd.Timestamp("2018-04-02 09:20:15,554").to_pydatetime()

'''
按时间段进行价格处理
处理后进行拼接
拼接注意事项:    
    在有删除操作时 保证拼接处的收益率
    价格不超过涨跌停
    成交量符合U型曲线

输入:
    待生成日
    源数据日序列
    源数据颗粒度需不大于需求精度
输出:
    按指定精度给出的行情数据
    源数据颗粒度需不大于指定精度
    
细节:
    先看old超出new部分有多少
    超出部分的量通过删掉1/2 压缩1/2进行处理 可以调节压缩删除比例
    删除压缩区别在于  删除是整段数据 也就是数个bar 压缩是去一个丢一个
    现在采取不区别两种删除的方式  也就是m个k线里面取n个
    arr = np.arange(10)
    np.random.shuffle(arr)
    arr
    
'''
class time_map(object):
    # pre: day 1min 6sec 500ms
    def set_pre(self,pre):
        self.pre=pre
    pass


class stock(object):
    pass



