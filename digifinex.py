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



def parse(exchange_id,exchange_name=file_name):

    my_format_obj = my_format()

    symbols_mq = my_mq(Symbols, Symbols, Symbols)
    tickers_mq = my_mq(TickerItem, TickerItem,TickerItem)

    ts = my_format_obj.get_13_str_time()
    tickers = []
    symbols =  []

    url = 'https://www.digifinex.com/'
    html = html_download(url)
    xml = etree.HTML(html)
    tr_list = xml.xpath("//div[@class='curView']//tr")
    for i in tr_list:
        subject = i.xpath("./@currency_trade")[0]
        subject = (subject.split('_')[1] + '^' +subject.split('_')[0]).upper()
        try:
            price = i.xpath(".//td[@class='rmb_pire_new']/a//span[@class='pire']/text()")[0]
        except:
            price = '0'
        unit = my_format_obj.get_unit(price)
        ticker_message = my_format_obj.format_tick(exchange_name, subject, exchange_id, price, unit, ts)
        tickers_mq.send_message(ticker_message)
        tickers.append(ticker_message)
        symbols.append(subject)


    symbols_message = my_format_obj.format_symbols(exchange_id, symbols, exchange_name)
    symbols_mq.send_message(symbols_message)
    print(symbols)
    print(tickers)
    return symbols ,tickers




if __name__ == '__main__':
    print(file_name,'\n')

    exchange_id = '106'
    parse(exchange_id)
