# -*- coding: utf-8 -*-
"""
Created on Tue Aug 14 14:23:17 2018

@author: admin
"""
import os
import sys
import platform
import numpy as np
win=True
if 'windows' not in platform.platform().lower():
    win=False
    sys.path.append('c:/code/python')
from fakequote import stock,date_map
from wutils import trade_date

ods=trade_date.getbizds(20180101,20180629)
nds=trade_date.getbizds(20200101,20200229)
dtmap=date_map(ods,nds,100)
ctrs=list()
with open('./stock_list.txt') as f:
    for ctr in f.readlines():
        ctrs.append(ctr.strip())
#ctrs=['000001']
for ctr in ctrs:
    try:
        pre_dict=dict()
        pre_dict['last_odt']=0
        pre_dict['pre_close']=0
        pre_dict['pre_close_old']=0
        for dt in nds:
            if win:
                ndir=f"./data/new/{dt}"
            else:
                ndir=f"../THS/fakequote/{dt}"
            if not os.path.isdir(ndir):
                os.mkdir(ndir)
            odts=dtmap[dt]

            zz=stock()
            zz.set_ctr(ctr)
            zz.set_today(str(dt))
            zz.ndir=ndir
            zz.set_date_range(dtmap[dt])
            zz.set_price_level(5)
            if pre_dict['last_odt']!=0:
                zz.pre(pre_dict)
            zz.load_histroy()
            zz.time_grep()
            zz.time_select()
            zz.conbine_bar()
            zz.timestamp_adj()
            zz.hl_limit_adj()
            zz.volume_adj()
            zz.to_csv()
            zz.post()
            pre_dict['last_odt']=odts[-1]
            pre_dict['pre_close']=zz.json['LastPrice']
            pre_dict['pre_close_old']=zz.json['old_LastPrice']
            print(zz.ctr,zz.today,pre_dict)
    except:
        pass
