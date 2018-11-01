import os
import json
import requests

from tools import my_mq, my_format ,json_download
from tools import DepthItem ,TickerItem ,TradeItem, Symbols 


file_name = os.path.basename(__file__).split('.')[0]
DepthItem = DepthItem + '_' + file_name
TickerItem = TickerItem + '_' + file_name
TradeItem = TradeItem + '_' + file_name
Symbols = Symbols + '_' + file_name


proxies = {
"http": "socks5://127.0.0.1:1080",
'https': 'socks5://127.0.0.1:1080'
}

cookies = {"__cfduid":"d1243dd0a0a1643738f73684a3aa9bbaf1540888884",
"USER_PW":"4f8ed331254239f6a5468307c80b21b4",
"PHPSESSID":"58ed771256004172c902a97054626351",
"languageStyle":"1",
"UM_distinctid":"166c4228e3c37c-0be604c3d8353c-346a7808-1fa400-166c4228e3db5c",
"_ga":"GA1.2.1272205097.1540888891",
"_gid":"GA1.2.1610023049.1540888891",
"__zlcmid":"p8hkov6SW4rHbY",
"lang":"zh_CN",
"CNZZDATA1273484625":"513997524-1540884947-https%253A%252F%252Fwww.coinegg.com%252F%7C1540946491",
"cf_clearance":"cf23cb98d3613f834837779fd32442ec4638ce8c-1540953285-900-150",}

headers = {
"user-agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36",
"accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
"referer":"https://www.coinegg.com/coin/btc/allcoin?t=0.4747793695398985",
"accept-encoding":"gzip, deflate, br",
"accept-language":"zh-CN,zh;q=0.9,en;q=0.8",    
}



def parse(exchange_id,exchange_name):

    symbols_mq = my_mq(Symbols, Symbols, Symbols)
    tickers_mq = my_mq(TickerItem, TickerItem,TickerItem)

    symbols_url = 'https://www.coinegg.com/coin/btc/allcoin?t=0.4747793695398985'

    # all_symbls = json_download(symbols_url,proxies=proxies)
    all_symbls = requests.get(symbols_url,cookies=cookies,headers=headers)
    print(all_symbls.text)
    # ts = get_13_str_time()
    # unit = '0.00000001'
    # for symbol in all_symbls['result']:
    #     price = symbol['last']
    #     subject = _Upper(symbol['symbol']).replace('_','^')
    #     symbols.append(subject)
    #     tick = format_tick(exchange_name, subject, exchange_id, price, unit, ts)
    #     ticker_messege = json.dumps(tick)
    #     send_mq(tickers_channel, message=ticker_messege, routing_key=TickerItem, exchange=TickerItem)
    #     ticks.append(tick)

    # symbols_messege = format_symbols(exchange_id, symbols, exchange_name)
    # symbols_messege = json.dumps(symbols_messege)
    # send_mq(symbols_channel, message=symbols_messege, routing_key=Symbols, exchange=Symbols)
    # print(symbols)
    # print(ticks)
    # return symbols ,ticks





if __name__ == '__main__':
    print(Symbols)
    print(TickerItem,'\n')

    exchange_id = '102'
    exchange_name = file_name
    parse(exchange_id, exchange_name)
