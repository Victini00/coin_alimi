import os
import time
import datetime

import ccxt # 암호화폐모듈
import pprint # 인쇄 방법 프리셋
import pandas as pd # 데이터프레임

from binance.client import Client
from binance.enums import *

# 환경변수
api_key = os.environ.get('BINANCE_API_KEY')
api_secret = os.environ.get('BINANCE_API_SECRET')

cli = Client(api_key, api_secret)

############## 수정 ###################
# 원하는 암호화폐 종류를 입력한다.
symbol = 'BTC/USDT'
# 시간 프레임 크기를 정한다. 1m, 1h, 1d,...
timeframe = '1m'


# 암호화폐 데이터 불러오기 --------------------
# 마켓 정보 불러오기
exchange = ccxt.binance(config={
    'apiKey' : api_key,
    'secret': api_secret,
    'enableRateLimit': True
    }
)

markets = exchange.load_markets()

# 현재가 조회 ---------------------------------

# 다양한 정보를 json 형태로 묶어 리턴해준다.
tickers = exchange.fetch_tickers()
BTC = tickers[symbol]

# 현재가는 티커의 close를 통해 얻을 수 있다.
# 시간은 timestamp로 얻을 수 있다. ms 단위.

# pprint.pprint(BTC)

# timestamp를 통해 시간 정보를 얻어온 후
# datetime으로 깔끔하게 바꿔줌
timestamp = BTC['timestamp'] / 1000
now_time = datetime.datetime.fromtimestamp(timestamp)

now_price = BTC['close'] # 달러 기준.

# print(now_price, timestamp, now_time)

# 호가 조회 ------------------------------------

order_book = exchange.fetch_order_book(symbol = symbol)
# pprint.pprint(order_book)

# 시세 캔들 조회 -------------------------------

# ohlcv: open, high, low, close, volume
ohlcv = exchange.fetch_ohlcv(symbol=symbol, timeframe=timeframe)






# 내 잔고 조회

# 선물 주문


