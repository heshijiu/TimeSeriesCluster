#!/usr/bin/Python
# -*- coding: utf-8 -*-
import tushare as ts
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime
import pywt
import sqlite3

AllStockFilePath = "AllStock.csv"
DBPATH = "D:\python_project\MyStockTest\dbs\\"

def GetAllStockCode():
    df = pd.read_csv(AllStockFilePath, dtype=str)
    codes = []
    for i in range(0, len(df)):
        code = df.loc[i, 'code']
        codes.append(code)
    return codes
def LoadAllStockDict():
    df = pd.read_csv(AllStockFilePath, dtype=str)
    stockDict = {}
    for i in range(0, len(df)):
        code = df.loc[i, 'code']
        name = df.loc[i, 'name']
        stockDict[code] = name
    return stockDict
class StockDataArray:
    stockCode = None
    dataArray = []
    def __init__(self, code = None, data = []):
        self.Clear()
        self.stockCode = code
        self.dataArray = data
        return
    def Clear(self):
        self.dataArray[:] = []

def GetStockSingleArray(stockCode = None, item = 'close', start='2017-01-04', end = '2017-01-05'):#item = 'open','high','close','low'
    singleArray = []
    if stockCode == None:
        return singleArray
    try:
        df = ts.get_k_data(stockCode, start=start, end=end)
    except:
        print("Read data failed")
    else:
        count = len(df[item])
        for i in range(0, count):
            singleArray.append(df[item][i])
    return singleArray

def GetStockPlotData(stockCode = None, item = 'close', start=None, end = None): # item = 'open','high','close','low'
    if stockCode == None or start == None or end == None:
        return None
    df = ts.get_hist_data(stockCode, start = start, end = end)
    data = {}
    data['date'] = list(df.index)
    if isinstance(item, list):
        for i in item:
            data[i] = list(df[i])
    else:
        data[item] = list(df[item])
    return data

def GetShiborData(item = None,year = 2017):# item = 'ON', '1W','2W','1M','6M','9M', '1Y'
    if item == None:
        return None
    df = ts.shibor_data(year)
    data = {}
    data['date'] = df['date']
    if isinstance(item, list):
        for i in item:
            data[i] = df[i]
    else:
        data[item] = df[item]
    return data
class singlTick:
    time = None
    price = 0
    volume = 0
    def __init__(self, time, price, volume):
        self.time = time
        self.price = price
        self.volume = volume
        return
class TickDate:
    tickDate = None
    tickList = None
    stockCode = None
    def __init__(self, stockCode = None, tickDate = None, type = 'online'):
        self.tickDate = tickDate
        self.stockCode = stockCode
        self.CreattickList(type)
        return
    def CreattickList(self, type = 'online'):
        if type == 'online':
            df = ts.get_tick_data(self.stockCode, self.tickDate)
        elif type == 'db':
            df = self.CreatDfFromDB()
        else:
            return None
        self.tickList = []
        for i in range(0, len(df)):
            time = df.loc[i, 'time']
            price = df.loc[i, 'price']
            volum = df.loc[i, 'volume']
            item = singlTick(time, price, volum)
            self.tickList.append(item)
        return
    def GetPriceArray(self):
        priceArray = []
        i = 0
        while i < len(self.tickList):
            priceArray.append(self.tickList[len(self.tickList) - 1 - i].price)
            i += 1
        return priceArray
    def CreatDf(self):
        if len(self.tickList) == 0:
            return None
        df = pd.DataFrame()
        time = []
        price = []
        volume = []
        for item in self.tickList:
            time.append(item.time)
            price.append(item.price)
            volume.append(item.volume)
        df['time'] = time
        df['price'] = price
        df['volume'] = volume
        return df
    def WriteToDB(self, dbName = None):
        if len(self.tickList) == 0:
            return
        if dbName == None:
            dbName = DBPATH + self.stockCode + '.sqlite'
        con = sqlite3.connect(dbName)
        df = self.CreatDf()
        try:
            df.to_sql(self.tickDate, con=con, flavor='sqlite', if_exists='replace', index=False)
        except:
            errorMessage = self.stockCode + self.tickDate + 'write to sql failed'
            print(errorMessage)
        con.close()
        return
    def CreatDfFromDB(self):
        dbName = DBPATH + self.stockCode + '.sqlite'
        con = sqlite3.connect(dbName)
        cur = con.cursor()
        sql = "SELECT count(*) FROM sqlite_master WHERE type='table' AND name=" + "'" + self.tickDate + "'"
        result = cur.execute(sql)
        count = result.fetchall()
        if int(count[0][0]) == 1:
            sql = "select * from" + " " + "'"+ self.tickDate + "'"
            df = pd.read_sql(sql, con)
        else:
            df = pd.DataFrame()
            print("No Such table in DB")
        con.close()
        return df
    def Simplify(self, level = None, ifNorm = True):
        single = self.GetPriceArray()
        count = len(single)
        if level == None:
            w = pywt.Wavelet('db1')
            maxLevel = pywt.dwt_max_level(count, w.dec_len)
            level = int(maxLevel / 2) + 1
        cA = pywt.wavedec(single, 'db1', level=level)
        newsingle = cA[0]
        radio = single[0]/newsingle[0]
        if ifNorm:
            return newsingle
        else:
            i = 0
            while i < len(newsingle):
                newsingle[i] *= radio
                i += 1
            return newsingle
    def Clear(self):
        self.tickList[:] = []
        self.tickDate = None
        self.stockCode = None
    def Plot(self):
        print(len(self.tickList))
        if len(self.tickList) == 0:
            return
        price = []
        time = []
        for item in self.tickList:
            price.append(item.price)
            timeStr = self.tickDate + ' '+ item.time
            time.append(datetime.datetime.strptime(timeStr, '%Y-%m-%d %H:%M:%S'))
        plt.plot(time, price)
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        #plt.show()
        return
    def Print(self):
        if len(self.tickList) == 0:
            return
        for item in self.tickList:
            print(item.time)
            print(item.price)
            print(item.volume)

def GetTickArray(code = None, date = None):
    if code == None or date == None:
        return None
    tick  = TickDate(code, date)
    return tick.GetPriceArray()

def CreatDatesByCode(stockCode = '002415',start = '2017-01-03', end = '2017-01-04'):
    df = ts.get_hist_data(stockCode, start=start, end=end)
    dateList = []
    for date in df.index:
        dateList.append(date)
    return dateList

if __name__ == "__main__":
    df = ts.shibor_data(2017)
    print(list(df.index))
