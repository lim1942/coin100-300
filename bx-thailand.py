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





def parse(exchange_id,exchange_name=file_name):

    my_format_obj = my_format()

    symbols_mq = my_mq(Symbols, Symbols, Symbols)
    tickers_mq = my_mq(TickerItem, TickerItem,TickerItem)

    ts = my_format_obj.get_13_str_time()
    tickers = []
    symbols =  []

    # 1
    url = 'https://bx.in.th/api/'
    cookies = {
    "__cfduid":"da186acb195967cb88968f2b757237afe1541146513",
    "cf_clearance":"6853d934e24912ff8eb325774587f540c5a64f29-1541146554-1800-250",
    "PHPSESSID":"q1chd9dcuc4tf1nr89lgq7r6ne"
    }
    res = json_download(url,cookies=cookies,headers=HEADERS)
    # 2
    res = res.values()
    for i in res:
        #3
        price = i["last_price"]
        #4
        subject = (i["secondary_currency"]+"^"+i["primary_currency"]).upper()
        symbols.append(subject)
        
        unit = my_format_obj.get_unit(price)
        ticker_message = my_format_obj.format_tick(exchange_name, subject, exchange_id, price, unit, ts)
        tickers_mq.send_message(ticker_message)
        tickers.append(ticker_message)


    symbols_message = my_format_obj.format_symbols(exchange_id, symbols, exchange_name)
    symbols_mq.send_message(symbols_message)

    print(symbols_message,'\n')
    print(tickers)
    return symbols ,tickers




if __name__ == '__main__':
    print(file_name,'\n')

    #5
    exchange_id = '129'
    parse(exchange_id)
