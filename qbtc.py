import os
import json
import requests

from tools import my_mq, my_format ,json_download
from tools import DepthItem ,TickerItem ,TradeItem, Symbols 


file_name = os.path.basename(__file__).split('.')[0]
DepthItem = DepthItem + '_' + file_name
TickerItem = TickerItem + '_' + file_name
TradeItem = TradeItem + '_' + file_name
Symbols = Symbols + '_' + file_name



def parse(exchange_id,exchange_name):

    headers = {
    "user-agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"
    }

    my_format_obj = my_format()

    symbols_mq = my_mq(Symbols, Symbols, Symbols)
    tickers_mq = my_mq(TickerItem, TickerItem,TickerItem)

    data = {"language":"en"}
    symbols_url = 'https://www.myqbtc.com/json/getAllCoinInfo.do'

    symbols = []
    tickers = []
    all_symbls = json_download(symbols_url,method='post',data=data,headers=headers)
    ts = my_format_obj.get_13_str_time()
    for symbol in all_symbls['result']:
        price = symbol['last']
        subject = symbol['symbol'].replace('_','^').upper()
        unit = my_format_obj.get_unit(price)
        symbols.append(subject)
        ticker_message = my_format_obj.format_tick(exchange_name, subject, exchange_id, price, unit, ts)
        tickers_mq.send_message(ticker_message)
        tickers.append(ticker_message)

    symbols_message = my_format_obj.format_symbols(exchange_id, symbols, exchange_name)
    symbols_mq.send_message(symbols_message)
    print(symbols)
    print(tickers)
    return symbols ,tickers




if __name__ == '__main__':
    print(Symbols)
    print(TickerItem,'\n')

    exchange_id = '101'
    exchange_name = 'qbtc'
    parse(exchange_id, exchange_name)
