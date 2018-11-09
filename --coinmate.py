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

rabbitmq_url = 'amqp://guest:123456@127.0.0.1:5672'


def parse(exchange_id,exchange_name=file_name):
    def inner_parse(subject):
        url = 'https://coinmate.io/api/ticker?currencyPair=' + subject.replace('^','_')
        res = json_download(url)['data']
        price =  res['last']
        ts = my_format_obj.get_13_str_time(res["timestamp"])
        unit = my_format_obj.get_unit(price)
        ticker_message = my_format_obj.format_tick(exchange_name, subject, exchange_id, price, unit, ts)
        tickers_mq.send_message(ticker_message)
        tickers.append(ticker_message)

    my_format_obj = my_format()
    symbols_mq = my_mq(Symbols, Symbols, Symbols)
    tickers_mq = my_mq(TickerItem, TickerItem,TickerItem)
    ts = my_format_obj.get_13_str_time()
    tickers = []
    symbols =  ["BTC^EUR","BTC^CZK","LTC^EUR","LTC^CZK","LTC^BTC","BCH^EUR","BCH^CZK","BCH^BTC","BTC^EUR","BTC^CZK","LTC^EUR","LTC^CZK","LTC^BTC","BCH^EUR","BCH^CZK","BCH^BTC"]


    symbols_message = my_format_obj.format_symbols(exchange_id, symbols, exchange_name)
    symbols_mq.send_message(symbols_message)
    gevent.joinall([gevent.spawn(inner_parse,subject) for subject in symbols])

    print(symbols_message,'\n')
    print(tickers)
    return symbols ,tickers


if __name__ == '__main__':
    print(file_name,'\n')
    exchange_id = '176'
    parse(exchange_id)
