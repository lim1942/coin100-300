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

rabbitmq_url = 'amqp://guest:123456@127.0.0.1:5672'



def parse(exchange_id,exchange_name=file_name):

    my_format_obj = my_format()
    symbols_mq = my_mq(Symbols, Symbols, Symbols,rabbitmq_url=rabbitmq_url)
    tickers_mq = my_mq(TickerItem, TickerItem,TickerItem,rabbitmq_url=rabbitmq_url)


    def get_symbols():
        map_dict = dict()
        url = 'https://kuna.io/api/v2/tickers'
        res = json_download(url)
        res = res.items()
        symbols = []
        for k,v in res:
            subject = k
            if subject.endswith('uah'):
                subject = subject.replace('uah','^uah')
            elif subject.endswith('btc'):
                subject = subject.replace('btc','^btc')
            elif subject.endswith('gbg'):
                subject = subject.replace('gbg','^gbg')
            elif subject.endswith('eurs'):
                subject = subject.replace('eurs','^eurs')
            subject = subject.upper()
            symbols.append(subject)
        symbols_message = my_format_obj.format_symbols(exchange_id, symbols, exchange_name)
        symbols_mq.send_message(symbols_message)
        print(symbols_message)
        return map_dict


    def get_tickers():
        url = 'https://kuna.io/api/v2/tickers'
        res = json_download(url)
        res = res.items()
        for k,v in res:
            subject = k
            if subject.endswith('uah'):
                subject = subject.replace('uah','^uah')
            elif subject.endswith('btc'):
                subject = subject.replace('btc','^btc')
            elif subject.endswith('gbg'):
                subject = subject.replace('gbg','^gbg')
            elif subject.endswith('eurs'):
                subject = subject.replace('eurs','^eurs')
            subject = subject.upper()
            price = v['ticker']['last']
            ts = my_format_obj.get_13_str_time(v['at'])
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
    print(file_name,'\n')
    #5
    exchange_id = '244'
    parse(exchange_id)
