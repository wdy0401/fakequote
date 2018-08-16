# -*- coding: utf-8 -*-
"""
Created on Tue Aug 14 14:23:17 2018

@author: admin
"""
import os
import sys
import platform
from fakequote import stock,date_map
if 'windows' in platform.platform().lower():
    sys.path.append('c:/code/python')
from wutils import trade_date

ods=trade_date.getbizds(20180101,20180629)
nds=trade_date.getbizds(20200101,20200229)
dtmap=date_map(ods,nds,100)
syms=['600000']
for sym in syms:
    pre_dict=dict()
    pre_dict['last_odt']=0
    pre_dict['pre_close']=0
    pre_dict['pre_close_old']=0
    for dt in nds:
        if dt>20200113:
            break
        ndir=f"./data/new/{dt}"
        if not os.path.isdir(ndir):
            os.mkdir(ndir)
        odts=dtmap[dt]

        zz=stock()
        zz.set_ctr(sym)
        zz.set_today(str(dt))
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
        print(pre_dict)
