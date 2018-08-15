#python -m unittest wtools.py
import unittest
import functools
import sys
from fakequote import date_map
'''
class TestDict(unittest.TestCase):
    def test_init(self):
        self.assertEqual(date_map(list(range(12)),list(range(5)),1), {0: [0, 1, 2, 3], 1: [4, 5], 2: [6, 7], 3: [8, 9], 4: [10, 11]})
'''

'''
import sqlite3
conn = sqlite3.connect('fakequote.db')
c=conn.cursor()
dts = [
    [20200101,'600000',20180101,20180104,5,5],
    [20200101,'600000',20180102,20180105,5,5],
    [20200101,'600000',20180101,20180104,10,10],]
dts=[tuple(x) for x in dts]
c.executemany('insert or replace into daily_price (date,ctr,bdate,edate,close,eclose) values (?,?,?,?,?,?)', dts)
conn.commit()
conn.close()
'''
class trade_date(object):
    def __init__(self):#交易和序号的对应关系
        re1=dict()
        with open("c:/code/bizd.txt") as f:
            for i,j in enumerate(f.readlines()):
                re1[int(j.strip())]=int(i)
                re2={v: k for k, v in re1.items()}
        self.ds=re1
        self.sd=re2
    def nextbizd(self,dt):
        dt=int(dt)
        while(dt<21000000):
            if dt in self.ds.keys():
                if self.ds[dt]+1 in self.sd.keys():
                    return self.sd[self.ds[dt]+1]
            else:
                dt+=1
        return 0
    def prebizd(self,dt):
        dt=int(dt)
        while(dt>20000000):
            if dt in self.ds.keys():
                if self.ds[dt]-1 in self.sd.keys():
                    return self.sd[self.ds[dt]-1]
            else:
                dt-=1
        return 0
    def isbizd(self,dt):
        if dt in self.ds.keys():
            return True
        else:
            return False

a=trade_date()
print(a.nextbizd(20180813))
print(a.nextbizd(20180100))

print(a.prebizd(20180813))
print(a.prebizd(20180100))

print(a.isbizd(20180813))
print(a.isbizd(20180100))
