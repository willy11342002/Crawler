import pandas as pd
import numpy as np
import pickle

# 使用pickle方式存資料, 預設使用HIGHEST_PROTOCOL是最高壓縮
# pickle是內建的套件, 貌似還有一種cpickle可以更快更好的壓縮, 但是需要另外安裝
def save_obj(obj, file, protocol = pickle.HIGHEST_PROTOCOL):
    with open(file, 'wb') as f:
        pickle.dump(obj, f, protocol)

# 這邊就更簡單了, 使用二進位方式讀取檔案並且回傳
def load_obj(file):
    with open(file, 'rb') as f:
        return pickle.load(f)

# 獲取某一檔股票的開高低收
def grep_stock(stock_no, dic, columns=None, sources=None):
    if not columns:
        columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    if not sources:
        sources = ['開盤價', '最高價', '最低價', '收盤價', '成交筆數']
            
    df = pd.DataFrame(columns=columns)
    for date, data in dic.items():
        if data is not None:
            df.loc[date] = dic[date].loc[stock_no, sources].tolist()
    
    df.index = df.index.astype(np.datetime64)
    for column in columns:
        df[column] = pd.to_numeric(df[column], errors='coerce')
    df.dropna(inplace=True)
    df.sort_index(inplace=True)
    
    return df
    
    
    
    