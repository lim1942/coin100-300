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
    headers = {
    "user-agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"
    }


    def get_symbols():
        map_dict = dict()
        data = {"language":"en"}
        symbols_url = 'https://www.myqbtc.com/json/getAllCoinInfo.do'
        all_symbls = json_download(symbols_url,method='post',data=data,headers=headers)
        res = all_symbls['result']
        symbols = []
        for i in res:
            price = i['last']
            subject = i['symbol'].replace('_','^').upper()
            symbols.append(subject)
        symbols_message = my_format_obj.format_symbols(exchange_id, symbols, exchange_name)
        symbols_mq.send_message(symbols_message)
        print(symbols_message)
        return map_dict


    def get_tickers():
        data = {"language":"en"}
        symbols_url = 'https://www.myqbtc.com/json/getAllCoinInfo.do'
        all_symbls = json_download(symbols_url,method='post',data=data,headers=headers)
        res = all_symbls['result']
        ts = my_format_obj.get_13_str_time()
        for i in res:
            price = i['last']
            subject = i['symbol'].replace('_','^').upper()
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
    print(Symbols)
    print(TickerItem,'\n')

    exchange_id = '101'
    exchange_name = 'qbtc'
    parse(exchange_id, exchange_name)
