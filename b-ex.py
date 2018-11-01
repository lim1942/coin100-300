import os
import json
import requests
from lxml import etree

from tools import my_mq, my_format ,json_download, html_download
from tools import DepthItem ,TickerItem ,TradeItem, Symbols 


file_name = os.path.basename(__file__).split('.')[0]
DepthItem = DepthItem + '_' + file_name
TickerItem = TickerItem + '_' + file_name
TradeItem = TradeItem + '_' + file_name
Symbols = Symbols + '_' + file_name




def handle_tickers(res):
    label_price_map = dict()
    for i in res:
        label_price_map[i['Label']] = i['LastPrice']
    return label_price_map



def parse(exchange_id,exchange_name=file_name):

    my_format_obj = my_format()

    symbols_mq = my_mq(Symbols, Symbols, Symbols)
    tickers_mq = my_mq(TickerItem, TickerItem,TickerItem)

    ts = my_format_obj.get_13_str_time()
    tickers = []
    symbols =  []

    url = 'https://b-ex.io/api/ticket'
    res = json_download(url)['data']
    for market,coin_list in res.items():
        market = market.split('_')[0]
        for coin in coin_list:
            price = coin["price"]
            subject = (coin["coin_name"] + '^' + market).upper()
            unit = my_format_obj.get_unit(price)
            ticker_message = my_format_obj.format_tick(exchange_name, subject, exchange_id, price, unit, ts)
            tickers_mq.send_message(ticker_message)
            tickers.append(ticker_message)
            symbols.append(subject)



    symbols_message = my_format_obj.format_symbols(exchange_id, symbols, exchange_name)
    symbols_mq.send_message(symbols_message)

    print(symbols_message,'\n')
    print(tickers)
    return symbols ,tickers




if __name__ == '__main__':
    print(file_name,'\n')

    exchange_id = '110'
    parse(exchange_id)
