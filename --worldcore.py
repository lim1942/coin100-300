import gevent
from gevent import monkey
monkey.patch_all()

import os
import json
import requests
from lxml import etree

from tools import my_mq, my_format ,json_download, html_download, my_websocket
from tools import DepthItem ,TickerItem ,TradeItem, Symbols ,SOCK_PROXIES, HEADERS

file_name = os.path.basename(__file__).split('.')[0]
DepthItem = DepthItem + '_' + file_name
TickerItem = TickerItem + '_' + file_name
TradeItem = TradeItem + '_' + file_name
Symbols = Symbols + '_' + file_name
cookies = {'auth_token':'332353c8-f49e-4a1c-9c17-cc348b0421d5'}


rabbitmq_url = 'amqp://guest:123456@127.0.0.1:5672'


def parse(exchange_id,exchange_name=file_name):
    def inner_parse(subject):
        url = 'https://api.worldcore.trade/history/trade?pair=' + subject.replace('^','_').lower()
        res = json_download(url,cookies=cookies)['result']['items'][0]
        price = res['price']
        unit = my_format_obj.get_unit(price)
        ticker_message = my_format_obj.format_tick(exchange_name, subject, exchange_id, price, unit, ts)
        tickers_mq.send_message(ticker_message)
        tickers.append(ticker_message)

    my_format_obj = my_format()
    symbols_mq = my_mq(Symbols, Symbols, Symbols)
    tickers_mq = my_mq(TickerItem, TickerItem,TickerItem)
    ts = my_format_obj.get_13_str_time()
    tickers = []
    symbols =  []
    url = 'https://api.worldcore.trade/market/pairs'
    res = json_download(url,cookies=cookies)
    res = res['result']['pairs']
    for i in res:
        subject = i['pair'].replace('_','^').upper()
        symbols.append(subject)

    symbols_message = my_format_obj.format_symbols(exchange_id, symbols, exchange_name)
    symbols_mq.send_message(symbols_message)
    gevent.joinall([gevent.spawn(inner_parse,subject) for subject in symbols])

    print(symbols_message,'\n')
    print(tickers)
    return symbols ,tickers


if __name__ == '__main__':
    print(file_name,'\n')
    #5
    exchange_id = '155'
    parse(exchange_id)
