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



get_ws_symbols = True
def parse(exchange_id,exchange_name=file_name):

    def on_message(ws, message):
        global get_ws_symbols
        content = json.loads(message)
        if content['action'] == "Pushdata.market":
            data = content['data']

            # for symbols
            if get_ws_symbols:
                symbols = []
                for k,v in data.items():
                    subject = k.replace('_','^').upper()
                    symbols.append(subject)
                symbols_message = my_format_obj.format_symbols(exchange_id, symbols, exchange_name)
                symbols_mq.send_message(symbols_message)
                print(symbols_message,'\n')
                get_ws_symbols = False

            # for tikers
            ts = my_format_obj.get_13_str_time(content['time'])
            for k,v in data.items():
                subject = k.replace('_','^').upper()
                price = v['l']
                unit = my_format_obj.get_unit(price)
                ticker_message = my_format_obj.format_tick(exchange_name, subject, exchange_id, price, unit, ts)
                tickers_mq.send_message(ticker_message)
                print(ticker_message)


    my_format_obj = my_format()
    symbols_mq = my_mq(Symbols, Symbols, Symbols,rabbitmq_url=rabbitmq_url)
    tickers_mq = my_mq(TickerItem, TickerItem,TickerItem,rabbitmq_url=rabbitmq_url)

    url = 'wss://wsv2.bit-z.pro/wss'
    message = '{"data":{"type":"market","dataType":"blob","nonce":"754940","_CDID":"100002","_CDCODE":"b9f71609a6174cf30b9344aeccc20e9c"},"msg_id":1539754940081,"action":"Topic.sub"}'
    a_web_socket = my_websocket()
    a_web_socket.get_a_ws(url, on_message, message)
    a_web_socket.run_always()



    # def get_symbols():
    #     map_dict = dict()
    #     # 1
    #     url = 
    #     res = json_download(url)
    #     # 2
    #     res = 
    #     symbols = []
    #     for i in res:
    #         #4
    #         subject = i[]
    #         symbols.append(subject)
    #     symbols_message = my_format_obj.format_symbols(exchange_id, symbols, exchange_name)
    #     symbols_mq.send_message(symbols_message)
    #     print(symbols_message)
    #     return map_dict


    # def get_tickers():
    #     # 1
    #     url = 
    #     res = json_download(url)
    #     # 2
    #     res = 
    #     ts = my_format_obj.get_13_str_time()
    #     for i in res:
    #         #3
    #         subject = i[]
    #         #4
    #         price = i[]
    #         # ts = my_format_obj.get_13_str_time(i[])
    #         unit = my_format_obj.get_unit(price)
    #         ticker_message = my_format_obj.format_tick(exchange_name, subject, exchange_id, price, unit, ts)
    #         tickers_mq.send_message(ticker_message)
    #         print(ticker_message)


    # while 1:
    #     try:    
    #         map_dict = get_symbols()
    #         while  1:
    #             try:
    #                 get_tickers()
    #             except Exception as e:
    #                 print('eid:',exchange_id,traceback.print_exc())
    #             time.sleep(1)
    #     except Exception as e:
    #         print('eid:', exchange_id, traceback.print_exc())
    #     time.sleep(1)



if __name__ == '__main__':
    exchange_id = 'null'
    parse(exchange_id)
