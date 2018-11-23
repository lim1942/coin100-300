import os
import json
import time
import requests
import traceback
from lxml import etree

from tools import my_mq, my_format ,json_download, html_download, my_websocket
from tools import DepthItem ,TickerItem ,TradeItem, Symbols ,SOCK_PROXIES, HEADERS

file_name = os.path.basename(__file__).split('.')[0]
DepthItem = DepthItem + '_' + file_name
TickerItem = TickerItem + '_' + file_name
TradeItem = TradeItem + '_' + file_name
Symbols = Symbols + '_' + file_name

#specify rabbit mq url
rabbitmq_url = 'amqp://guest:123456@127.0.0.1:5672'



def parse(exchange_id,exchange_name=file_name):

    my_format_obj = my_format()
    symbols_mq = my_mq(Symbols, Symbols, Symbols,rabbitmq_url=rabbitmq_url)
    tickers_mq = my_mq(TickerItem, TickerItem,TickerItem,rabbitmq_url=rabbitmq_url)


    def get_symbols():
        map_dict = dict()
        # 1 config symbols url
        url1 = 'https://9coin.com/trade/menu/middle/trade/group/change?currency_group=1&l=en-us'
        url2 = 'https://9coin.com/trade/menu/middle/trade/group/change?currency_group=2&l=en-us'
        url3 = 'https://9coin.com/trade/menu/middle/trade/group/change?currency_group=3&l=en-us'
        res1 = json_download(url1,proxies=SOCK_PROXIES)['data']
        res2 = json_download(url2,proxies=SOCK_PROXIES)['data']
        res3 = json_download(url3,proxies=SOCK_PROXIES)['data']
        # 2 config symbols result
        res = res1 + res2 + res3
        symbols = []
        for i in res:
            #3 config symbols subject
            subject = i['cy_mark'].replace('/','^')
            symbols.append(subject)
        symbols_message = my_format_obj.format_symbols(exchange_id, symbols, exchange_name)
        symbols_mq.send_message(symbols_message)
        print(symbols_message)
        return map_dict


    def get_tickers():
        # 4 config tikers url
        url1 = 'https://9coin.com/trade/menu/middle/trade/group/change?currency_group=1&l=en-us'
        url2 = 'https://9coin.com/trade/menu/middle/trade/group/change?currency_group=2&l=en-us'
        url3 = 'https://9coin.com/trade/menu/middle/trade/group/change?currency_group=3&l=en-us'
        res1 = json_download(url1,proxies=SOCK_PROXIES)['data']
        res2 = json_download(url2,proxies=SOCK_PROXIES)['data']
        res3 = json_download(url3,proxies=SOCK_PROXIES)['data']
        # 5 config tickers result
        res = res1 + res2 + res3
        ts = my_format_obj.get_13_str_time()
        for i in res:
            # 6 config tickers subject
            subject = i['cy_mark'].replace('/','^')
            # 7 config tickers price
            price = i['new_price']
            # ts = my_format_obj.get_13_str_time(i[])
            unit = my_format_obj.get_unit(price)
            ticker_message = my_format_obj.format_tick(exchange_name, subject, exchange_id, price, unit, ts)
            tickers_mq.send_message(ticker_message)
            print(ticker_message)


    while 1:
        try:    
            map_dict = get_symbols()
            while  1:
                try:
                    get_tickers()
                except Exception as e:
                    print('eid:',exchange_id,traceback.print_exc())
                time.sleep(1)
        except Exception as e:
            print('eid:', exchange_id, traceback.print_exc())
        time.sleep(1)



if __name__ == '__main__':
    # 0 config market`s exchange_id
    exchange_id = '107'
    parse(exchange_id)
