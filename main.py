import os
import time
import datetime

import ccxt # 암호화폐모듈
import ccxt.pro as ccxtpro # 웹소켓용 pro module
import pprint # 인쇄 방법 프리셋
import pandas as pd # 데이터프레임

from binance.client import Client
from binance.enums import *

import telegram_message as tele_talk

# 환경변수
api_key = os.environ.get('BINANCE_API_KEY')
api_secret = os.environ.get('BINANCE_SECRET_KEY')

cli = Client(api_key, api_secret)

############## 수정 ###################
# 원하는 암호화폐 종류를 입력한다.
symbol = "BTC/USDT"
# 시간 프레임 크기를 정한다. 1m, 1h, 1d,...
timeframe = '4h'
# RSI limit, 몇 개를 가지고 계산할지
limit = 200
# RSI period, 기본값은 14
period = 14
RSI_upper_line = 75
RSI_lower_line = 25
#######################################

### 중요 ###
# 암호화폐 데이터 불러오기 --------------------
# 마켓 정보 불러오기
# 웹소켓이면, ccxtpro.binance로 사용한다.
exchange = ccxt.binance(config={
    'apiKey' : api_key,
    'secret': api_secret,
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future'
    }
})

markets = exchange.load_markets()

# 현재가 조회 -----------------------------------------------

# 다양한 정보를 json 형태로 묶어 리턴해준다.
# tickers = exchange.fetch_tickers()

BTC = exchange.fetch_ticker(symbol)

# 현재가는 티커의 close를 통해 얻을 수 있다.
# 시간은 timestamp로 얻을 수 있다. ms 단위.
# pprint.pprint(BTC)
# timestamp를 통해 시간 정보를 얻어온 후, datetime으로 깔끔하게 바꿔줌
timestamp = BTC['timestamp'] / 1000
now_time = datetime.datetime.fromtimestamp(timestamp)

now_price = BTC['close'] # 달러 기준.

print(now_price, timestamp, now_time)

# 호가 조회 -------------------------------------------------

order_book = exchange.fetch_order_book(symbol = symbol)
# pprint.pprint(order_book)

# 시세 캔들 조회 ---------------------------------------------

# ohlcv: open, high, low, close, volume
# limit 인자를 주면, 몇 개의 데이터를 가져올지 설정할 수 있다.
ohlcv = exchange.fetch_ohlcv(symbol=symbol, timeframe=timeframe, limit=limit)
df = pd.DataFrame(ohlcv)

'''
df = pd.DataFrame(btc_ohlcv, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')
df.set_index('datetime', inplace=True)
print(df)
'''

# 내 잔고 조회 ------------------------------------------------
# free, total, used 총 3개의 옵션이 있다.
balance = exchange.fetch_balance()
my_USDT_balance = balance['USDT']

# pprint.pprint(my_USDT_balance)
# print(my_USDT_balance.get('free'))



# 주문(선물 시장) -----------------------------------------------

# 레버리지 설정
# exchange.set_leverage(배율, symbol)

# 모드 설정(교차, 격리)
# exchange.set_margin_mode(marginMode='cross' or 'isolated', symbol)

# Funding Fee
# exchange.fetch_funding_rate(symbol=symbol)
# pprint.pprint(resp)

# {시장가, 지정가}, {롱, 숏} 옵션을 선택할 수 있다.
# TP / SL 옵션도 선택할 수 있다. -> 실현될 경우, 반대 주문은 자동으로 취소된다.

    # create_{market, limit}_{buy, sell}_order(symbol, amount, price(limit일 때), params)
    # camelCase도 있다. createMarketOrder로 buy, sell을 param으로 넘길 수도 있다.
    # https://docs.ccxt.com/#/

'''
    예시 1: create_order 함수로 주문
    order1 = binance.create_order(
                symbol = "BTC/USDT",
                type = "MARKET",
                side = "buy",
                amount = 0.0001
            )

    예시 2: 예시 1의 주문을 TP하는 주문
    order2 = binance.create_order(
                symbol = "BTC/USDT",
                type = "TAKE_PROFIT_MARKET",
                side = "sell",
                amount = 0.0001,
                params={'stopPrice': 55000}
            )

    예시 3: create_limit_sell_order 함수 사용하여 주문
    order3 = binance.create_limit_sell_order(
                symbol = "ETH/USDT",
                amount = 0.1,
                price = 3000,
            )

    # pprint.pprint(order)
'''

# 현재 포지션을 불러올 수 있다.
# json 형태로 리턴된다.
    # exchange.fetch_positions(symbol=symbol)


# 대기 주문(Open Orders)을 불러올 수 있다.
# 여러 개의 주문은 json(파이썬 딕셔너리) 형태의 리스트로 리턴된다.

    # open_orders_list = exchange.fetch_open_orders(symbol = "어쩌구/USDT")
    # pprint.pprint(open_orders_list)

# 특정 심볼의 대기 주문 취소

    # 1. 특정 심볼의 대기 주문 전체 취소
    # exchange.cancel_all_orders(symbol = "어쩌구/USDT")

    # 2. 특정 심볼의 특정 대기 주문 취소
    # 이 경우, id를 알아야 한다.
    # exchange.cancel_order(id = id, symbol = "어쩌구/USDT")


# 보조 지표 ----------------------------------------------------
# 1. RSI / divergence

# 기본 설정으로, 14일에 대해 구하기 때문에, period를 14로 설정
def RSI_calculator(df: pd.DataFrame, period: int = period):
    ohlcv_close = df[4].astype(float) 
    # ohlcv의 data는 앞에서부터 'datetime', 'open', 'high', 'low', 'close', 'volume'
    # 따라서 close, 종가를 가져와 float으로 변환하게 된다.
    diff = ohlcv_close.diff() # pandas의 행끼리의 차이를 기록하는 함수.
    gain, decline = diff.copy(), diff.copy() # 상승하락을 따로 계산하기 위해 복사.
    gain[gain < 0] = 0
    decline[decline > 0] = 0

    _gain = gain.ewm(com=(period - 1), min_periods=period).mean()
    _loss = decline.abs().ewm(com=(period - 1), min_periods=period).mean()

    RS = _gain / _loss
    return pd.Series(100 - (100 / (1 + RS)), name = "RSI")


def now_RSI(timeframe = timeframe, symbol = symbol):
    return RSI_calculator(df, period).iloc[-1]

def RSI_list(timeframe = timeframe, symbol = symbol):
    return RSI_calculator(df, period)

# 특정 타임프레임에서의 rsi값 구하기
# print(now_RSI(timeframe='15m'))

# 하락 다이버전스
# RSI_list(timeframe, symbol)[17] ,print(ohlcv)
# 실질적으로 계산하는 캔들 수는, {limit - period}개이다.

def find_short_divergence(symbol = symbol, timeframe = timeframe, limit = limit, period = period):
    # initialize
    divergence_list = []
    divergence_count = 0

    temp_datetime = datetime.datetime.fromtimestamp(ohlcv[period][0]/1000) # time

    max_price = ohlcv[period][2] # high price
    # min_price = ohlcv[period][3] # low price

    rsi = RSI_list(timeframe, symbol)[period]

    for i in range(period+1, limit-1):
        this_max_price = ohlcv[i][2]
        this_rsi = RSI_list(timeframe, symbol)[i]
        this_time = datetime.datetime.fromtimestamp(ohlcv[i][0]/1000)

        # 현재 rsi가 지역 최적해임과 동시에, 과매수 구간인 경우
        if this_rsi >= RSI_list(timeframe, symbol)[i-1] and this_rsi >= RSI_list(timeframe, symbol)[i+1] and this_rsi >= RSI_upper_line:
            if rsi < RSI_upper_line:
                rsi = RSI_list(timeframe, symbol)[i]
                max_price = this_max_price
                temp_datetime = this_time
            # 이하의 경우는 rsi와 this_rsi가 전부 RSI_upper_line 이상.
            elif this_max_price > max_price and this_rsi < rsi: # regular divergence
                divergence_count += 1
                divergence_list.append([temp_datetime, this_time, "일반 하락 다이버전스"])

                rsi = RSI_list(timeframe, symbol)[i]
                max_price = this_max_price
                temp_datetime = this_time
            elif this_max_price < max_price and this_rsi > rsi: # hidden divergence
                divergence_count += 1
                divergence_list.append([temp_datetime, this_time, "히든 하락 다이버전스"])

                rsi = RSI_list(timeframe, symbol)[i]
                max_price = this_max_price
                temp_datetime = this_time
    
    return divergence_list

# print(find_short_divergence(symbol, timeframe, limit, period))

##################################################################
# 프로 웹소켓 모듈
# 다양한 모듈이 있음. exchange.has['...'] 명령어로 지원여부를 확인할 수 있다.



##################################################################
# 메세지 보내기 모듈

# 1. 하락 다이버전스 알림
div_list = find_short_divergence(symbol, timeframe, limit, period)
mess = ("[다이버전스 알림] "+  str(timeframe) + " timeframe 기준으로 최근 " + str(limit) + "캔들 중 " + 
        str(len(div_list)) + "번의 하락 다이버전스가 발생하였습니다. 가장 최신 하락 다이버전스는 " + 
        str(div_list[-1][0]) + "과 " + str(div_list[-1][1]) + "사이의 " + div_list[-1][2] + "입니다.")
tele_talk.send_message(mess)



