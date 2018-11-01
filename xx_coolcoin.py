import os
import json
import requests
requests.packages.urllib3.disable_warnings()

from tools import my_mq, my_format ,json_download,html_download
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
    
cookies = {"__cfduid":"d12e7a9603377fb3638df5d7da50cda881540956579",
"USER_PW":"fc0cd485ee7dfeec2520cbee6eb3151a",
"PHPSESSID":"9a0068b7560450cb2511f67fc0d06f21",
"languageStyle":"1",
"lang":"zh_CN",
"_ga":"GA1.2.159973335.1540956582",
"_gid":"GA1.2.1866093378.1540956582",}

headers = {
"accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
"accept-encoding":"gzip, deflate, br",
"accept-language":"zh-CN,zh;q=0.9,en;q=0.8",
"upgrade-insecure-requests":"1",
"user-agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36",  
"x-requested-with":"XMLHttpRequest"
}



def parse(exchange_id,exchange_name):

    symbols_mq = my_mq(Symbols, Symbols, Symbols)
    tickers_mq = my_mq(TickerItem, TickerItem,TickerItem)

    s = requests.Session()
    s.get('https://www.coolcoin.com/',headers=headers,proxies=proxies,verify=False)

    btc_url = 'https://www.coolcoin.com/coin/btc/allcoin'
    all_symbls = s.get(btc_url)

    # usdt_url = 'https://www.coolcoin.com/coin/usdt/allcoin'
    # all_symbls = json_download(usdt_url)

    print(all_symbls)

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
