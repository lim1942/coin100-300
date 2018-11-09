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


headers = {
"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36",
"authorization":"Basic Y29tLmJldC53ZWI6NkVENUM0NzgxRjNBNEM4MkI2Njg5OTkxN0Q2Nzc4NEU=",
"client-device": "761fe955ee05c3f9dfe241af2633fbcd",
"client-id": "com.bet.web",
"client-version": "1.0.0",
}



def parse(exchange_id,exchange_name=file_name):

    my_format_obj = my_format()
    symbols_mq = my_mq(Symbols, Symbols, Symbols,rabbitmq_url=rabbitmq_url)
    tickers_mq = my_mq(TickerItem, TickerItem,TickerItem,rabbitmq_url=rabbitmq_url)


    def get_symbols():
        map_dict = dict()
        url = 'https://api.be.top/api/market/qutn/group'
        res = json_download(url,headers=headers)
        res =  res['data'][0]['items'] + res['data'][1]['items']+res['data'][2]['items']
        symbols = []
        for i in res:
            subject = i['name'].replace('/','^').upper() 
            symbols.append(subject)
        symbols_message = my_format_obj.format_symbols(exchange_id, symbols, exchange_name)
        symbols_mq.send_message(symbols_message)
        print(symbols_message)
        return map_dict


    def get_tickers():
        url = 'https://api.be.top/api/market/qutn/group'
        res = json_download(url,headers=headers)
        res = res['data'][0]['items'] + res['data'][1]['items']+res['data'][2]['items']
        ts = my_format_obj.get_13_str_time()
        for i in res:
            price = i['price']
            subject = i['name'].replace('/','^').upper() 
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
    print(file_name,'\n')

    #5
    exchange_id = '151'
    parse(exchange_id)
