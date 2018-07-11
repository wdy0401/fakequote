#-*- coding: utf-8 -*-
import pandas as pd
import datetime
import os

#根据分笔成交数据生成1分钟线
def gen_min_line(symbol, date):
    data_dir = '/home/vnpy/share/'
    str_date=str(date)
    dir=data_dir+symbol+'/'+str(date.year)+'/'+str(date.month)
    tickfile=dir+'/'+symbol+'_'+str_date+'.csv'
    minfile=dir+'/'+symbol+'_'+str_date+'_1m.csv'
    print tickfile,minfile
    if (os.path.exists(tickfile)) and (not os.path.exists(minfile)):
        df=pd.read_csv(tickfile)
        print "Successfully read tick file: "+tickfile
        if df.shape[0]<10: #TuShare即便在停牌期间也会返回tick data，并且只有三行错误的数据，这里利用行数小于10把那些unexpected tickdata数据排除掉
            print "No tick data read from tick file, skip generating 1min line"
            return 0
        df['time']=str_date+' '+df['time']
        df['time']=pd.to_datetime(df['time'])
        df=df.set_index('time')
        price_df=df['price'].resample('1min').ohlc()
        price_df=price_df.dropna()
        vols=df['volume'].resample('1min').sum()
        vols=vols.dropna()
        vol_df=pd.DataFrame(vols,columns=['volume'])
        amounts=df['amount'].resample('1min').sum()
        amounts=amounts.dropna()
        amount_df=pd.DataFrame(amounts,columns=['amount'])
        newdf=price_df.merge(vol_df, left_index=True, right_index=True).merge(amount_df, left_index=True, right_index=True)
	newdf.to_csv(minfile)
        print "Successfully write to minute file: "+minfile
  
dates=get_date_list(datetime.date(2018,1,1), datetime.date(2018,7,9))
stocks=get_all_stock_id()
for stock in stocks:
    for date in dates:
	gen_min_line(stock, date)
