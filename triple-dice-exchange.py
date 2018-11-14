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


data = '{"CGCBTC":{"tradedCcy":"CGC","settlementCcy":"BTC"},"CGCDDC":{"tradedCcy":"CGC","settlementCcy":"DDC"},"CGCDOGE":{"tradedCcy":"CGC","settlementCcy":"DOGE"},"CGCETH":{"tradedCcy":"CGC","settlementCcy":"ETH"},"CGCFOC":{"tradedCcy":"CGC","settlementCcy":"FOC"},"CGCLGC":{"tradedCcy":"CGC","settlementCcy":"LGC"},"CGCLTC":{"tradedCcy":"CGC","settlementCcy":"LTC"},"CGCSTART":{"tradedCcy":"CGC","settlementCcy":"START"},"CGCXRP":{"tradedCcy":"CGC","settlementCcy":"XRP"},"DDCBTC":{"tradedCcy":"DDC","settlementCcy":"BTC"},"DDCETH":{"tradedCcy":"DDC","settlementCcy":"ETH"},"DDCFOC":{"tradedCcy":"DDC","settlementCcy":"FOC"},"DDCKDC":{"tradedCcy":"DDC","settlementCcy":"KDC"},"DDCLTC":{"tradedCcy":"DDC","settlementCcy":"LTC"},"DDCOCZ":{"tradedCcy":"DDC","settlementCcy":"OCZ"},"DOGEBTC":{"tradedCcy":"DOGE","settlementCcy":"BTC"},"DOGEGLC":{"tradedCcy":"DOGE","settlementCcy":"GLC"},"ETHBTC":{"tradedCcy":"ETH","settlementCcy":"BTC"},"FOCBTC":{"tradedCcy":"FOC","settlementCcy":"BTC"},"FOCDOGE":{"tradedCcy":"FOC","settlementCcy":"DOGE"},"FOCETH":{"tradedCcy":"FOC","settlementCcy":"ETH"},"FOCGLC":{"tradedCcy":"FOC","settlementCcy":"GLC"},"FOCKDC":{"tradedCcy":"FOC","settlementCcy":"KDC"},"FOCLGC":{"tradedCcy":"FOC","settlementCcy":"LGC"},"FOCOCZ":{"tradedCcy":"FOC","settlementCcy":"OCZ"},"GLCBTC":{"tradedCcy":"GLC","settlementCcy":"BTC"},"GLCCGC":{"tradedCcy":"GLC","settlementCcy":"CGC"},"GLCDDC":{"tradedCcy":"GLC","settlementCcy":"DDC"},"GLCETH":{"tradedCcy":"GLC","settlementCcy":"ETH"},"GLCSTART":{"tradedCcy":"GLC","settlementCcy":"START"},"KDCBTC":{"tradedCcy":"KDC","settlementCcy":"BTC"},"KDCCGC":{"tradedCcy":"KDC","settlementCcy":"CGC"},"KDCETH":{"tradedCcy":"KDC","settlementCcy":"ETH"},"KDCGLC":{"tradedCcy":"KDC","settlementCcy":"GLC"},"KDCOCZ":{"tradedCcy":"KDC","settlementCcy":"OCZ"},"LGCBTC":{"tradedCcy":"LGC","settlementCcy":"BTC"},"LGCDDC":{"tradedCcy":"LGC","settlementCcy":"DDC"},"LGCETH":{"tradedCcy":"LGC","settlementCcy":"ETH"},"LGCGLC":{"tradedCcy":"LGC","settlementCcy":"GLC"},"LGCKDC":{"tradedCcy":"LGC","settlementCcy":"KDC"},"LGCOCZ":{"tradedCcy":"LGC","settlementCcy":"OCZ"},"LTCBTC":{"tradedCcy":"LTC","settlementCcy":"BTC"},"LTCGLC":{"tradedCcy":"LTC","settlementCcy":"GLC"},"NESBTC":{"tradedCcy":"NES","settlementCcy":"BTC"},"NESETH":{"tradedCcy":"NES","settlementCcy":"ETH"},"SKBBTC":{"tradedCcy":"SKB","settlementCcy":"BTC"},"SKBCGC":{"tradedCcy":"SKB","settlementCcy":"CGC"},"SKBDDC":{"tradedCcy":"SKB","settlementCcy":"DDC"},"SKBDOGE":{"tradedCcy":"SKB","settlementCcy":"DOGE"},"SKBETH":{"tradedCcy":"SKB","settlementCcy":"ETH"},"SKBFOC":{"tradedCcy":"SKB","settlementCcy":"FOC"},"SKBGLC":{"tradedCcy":"SKB","settlementCcy":"GLC"},"SKBKDC":{"tradedCcy":"SKB","settlementCcy":"KDC"},"SKBLGC":{"tradedCcy":"SKB","settlementCcy":"LGC"},"SKBLTC":{"tradedCcy":"SKB","settlementCcy":"LTC"},"SKBOCZ":{"tradedCcy":"SKB","settlementCcy":"OCZ"},"SKBSTART":{"tradedCcy":"SKB","settlementCcy":"START"},"SKBXRP":{"tradedCcy":"SKB","settlementCcy":"XRP"},"STARTBTC":{"tradedCcy":"START","settlementCcy":"BTC"},"XRPBTC":{"tradedCcy":"XRP","settlementCcy":"BTC"},"XRPGLC":{"tradedCcy":"XRP","settlementCcy":"GLC"},"XRPOCZ":{"tradedCcy":"XRP","settlementCcy":"OCZ"}}'



def parse(exchange_id,exchange_name=file_name):

    my_format_obj = my_format()
    symbols_mq = my_mq(Symbols, Symbols, Symbols,rabbitmq_url=rabbitmq_url)
    tickers_mq = my_mq(TickerItem, TickerItem,TickerItem,rabbitmq_url=rabbitmq_url)


    def get_symbols():
        map_dict = dict()
        # 1
        url = 'https://mydicewallet.com/moon/v1/composite/tickerData'
        res = json_download(url,method='post',data=data)
        # 2
        res = res['data'].items()
        symbols = []
        for k,v in res:
            #4
            subject = (k[:3]+'^' +k[3:]).upper()
            symbols.append(subject)
        symbols_message = my_format_obj.format_symbols(exchange_id, symbols, exchange_name)
        symbols_mq.send_message(symbols_message)
        print(symbols_message)
        return map_dict


    def get_tickers():
        # 1
        url = 'https://mydicewallet.com/moon/v1/composite/tickerData'
        res = json_download(url,method='post',data=data)
        # 2
        res = res['data'].items()  
        ts = my_format_obj.get_13_str_time()
        for k,v in res:
            #3
            subject = (k[:3]+'^' +k[3:]).upper()
            #4
            price = v['lastPrice']
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
    exchange_id = '238'
    parse(exchange_id)
