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



all_symbols = {"16":"EOS/ETH","79":"ETH/USDT","17":"RDN/ETH","19":"ZRX/ETH","113":"BTC/USDT","21":"HOT/ETH","22":"CVT/ETH","23":"GET/ETH","24":"LND/ETH","25":"SS/ETH","26":"BZNT/ETH","27":"TAU/ETH","28":"PAL/ETH","29":"SKM/ETH","30":"LBA/ETH","31":"ELI/ETH","32":"SNTR/ETH","33":"PCH/ETH","34":"HER/ETH","35":"EXC/ETH","36":"ICST/ETH","37":"UBT/ETH","38":"OMX/ETH","39":"IOTX/ETH","40":"HOLD/ETH","41":"VNT/ETH","42":"CAI/ETH","43":"ALI/ETH","44":"VITE/ETH","45":"EDR/ETH","46":"NKN/ETH","47":"SOUL/ETH","48":"Seele/ETH","49":"NRVE/ETH","50":"PAI/ETH","51":"BQT/ETH","53":"MT/ETH","54":"LEMO/ETH","55":"ABYSS/ETH","56":"QKC/ETH","57":"XPX/ETH","58":"MVP/ETH","59":"ATMI/ETH","60":"PKC/ETH","61":"GO/ETH","62":"RMESH/ETH","63":"UPP/ETH","64":"YEED/ETH","65":"FTM/ETH","66":"OLT/ETH","67":"DAG/ETH","68":"MET/ETH","69":"EGT/ETH","70":"KNT/ETH","71":"ZCN/ETH","72":"ZXC/ETH","73":"CARD/ETH","74":"MFT/ETH","75":"GOT/ETH","76":"AION/ETH","77":"ESS/ETH","78":"ZP/ETH","80":"BOX/ETH","82":"RHOC/ETH","83":"SPRK/ETH","84":"SDS/ETH","86":"ABL/ETH","87":"HIT/ETH","88":"PMA/ETH","89":"ACAD/ETH","90":"DX/ETH","92":"USE/ETH","93":"FOAM/ETH","94":"LX/ETH","95":"DAV/ETH","96":"PATH/ETH","97":"UBEX/ETH","98":"UCN/ETH","99":"ASA/ETH","100":"EDN/ETH","101":"META/ETH","102":"TXN/ETH","103":"DEC/ETH","104":"PAX/ETH","105":"GUSD/ETH","106":"USDC/ETH","107":"TOL/ETH","108":"NRP/ETH","109":"HUM/ETH","110":"LQD/ETH","111":"HQT/ETH","112":"PTN/ETH","114":"PTON/ETH","115":"MCC/ETH","116":"SOLVE/ETH","117":"TRTL/BTC"}


def parse(exchange_id,exchange_name=file_name):

    my_format_obj = my_format()

    symbols_mq = my_mq(Symbols, Symbols, Symbols)
    tickers_mq = my_mq(TickerItem, TickerItem,TickerItem)

    ts = my_format_obj.get_13_str_time()
    tickers = []
    symbols =  []

    # 1
    url = 'https://api.bilaxy.com/v1/tickers'
    res = json_download(url)
    # 2
    res = res['data']
    for i in res:
        #3
        price = i['last']
        #4
        subject = all_symbols[str(i['symbol'])]
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
    exchange_id = '146'
    parse(exchange_id)
