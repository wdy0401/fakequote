#python -m unittest wtools.py
import unittest
import functools
import sys
from fakequote import date_map

class TestDict(unittest.TestCase):
    def test_init(self):
        self.assertEqual(date_map(list(range(12)),list(range(5)),1), {0: [0, 1, 2, 3], 1: [4, 5], 2: [6, 7], 3: [8, 9], 4: [10, 11]})


import sqlite3
conn = sqlite3.connect('fakequote.db')
c=conn.cursor()
dts = [
    [20200101,'600000',20180101,20180104,5,5],
    [20200101,'600000',20180102,20180105,5,5],
    [20200101,'600000',20180101,20180104,10,10],]
dts=[tuple(x) for x in dts]
c.executemany('insert or replace  INTO daily_price (date,ctr,bdate,edate,close,eclose)  VALUES (?,?,?,?,?,?)', dts)
conn.commit()
conn.close()
