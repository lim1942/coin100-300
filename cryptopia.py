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

    symbols_url = 'https://www.cryptopia.co.nz/api/GetTradePairs'
    symbols_res = json_download(symbols_url)
    tickers_url =   'https://www.cryptopia.co.nz/api/GetMarkets'
    tickers_res = handle_tickers(json_download(tickers_url)['Data'])
    for i in symbols_res["Data"]:
        Label = i['Label']

        price = my_format_obj.conver_num_math(tickers_res[Label])
        unit = my_format_obj.get_unit(price)
        subject = Label.replace('/','^').upper()
        ticker_message = my_format_obj.format_tick(exchange_name, subject, exchange_id, price, unit, ts)
        tickers_mq.send_message(ticker_message)
        tickers.append(ticker_message)
        symbols.append(subject)


    symbols_message = my_format_obj.format_symbols(exchange_id, symbols, exchange_name)
    symbols_mq.send_message(symbols_message)

    print(symbols,'\n')
    print(tickers)
    return symbols ,tickers




if __name__ == '__main__':
    print(file_name,'\n')

    exchange_id = '108'
    parse(exchange_id)
