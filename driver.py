# -*- coding: utf-8 -*-
"""
Created on Tue Aug 14 14:23:17 2018

@author: admin
"""
import os
import sys
from fakequote import stock,date_map
sys.path.append('c:/code/python')
from wutils import trade_date

ods=trade_date.getbizds(20180101,20180629)
nds=trade_date.getbizds(20200101,20200229)
dtmap=date_map(ods,nds,10086)
syms=['600000']
for sym in syms:
    lastodt=0
    for dt in nds:
        ndir=f"./data/fkndt/{dt}"
        os.mkdir(ndir)
        odts=dtmap[dt]
        zz=stock()
        zz.set_today(dt)
        zz.pre("./a.json")
        zz.set_ctr(sym)
        zz.set_date_range(odts)
        zz.set_price_level(5)
        zz.load_histroy()
        zz.time_grep()
        zz.time_select()
        zz.conbine_bar()
        zz.timestamp_adj()
        zz.hl_limit_adj()
        zz.volume_adj()
        zz.to_csv(f"{ndir}/{sym}.csv")
        zz.post()
        lastodt=odts[-1]
        print(lastodt)
        break