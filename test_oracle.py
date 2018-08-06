# -*- coding: utf-8 -*-
"""
Created on Tue Jul 24 10:27:49 2018

@author: admin
"""
#python -m pip install cx_Oracle --upgrade
import cx_Oracle
 
#建立和数据库系统的连接
conn = cx_Oracle.connect('reader_wind','reader','10.189.65.33:1521/ORCL')
#获取操作游标
cursor = conn.cursor()
#执行SQL,创建一个表
cursor.execute("select * from wind")
#关闭连接，释放资源
fet=cursor.fetchall()
#执行完成，打印提示信息
print(fet)
