import re
import time
import json
import pika
import math
import requests
import traceback
import websocket

requests.packages.urllib3.disable_warnings()



rabbitmq_url = 'amqp://guest:123456@127.0.0.1:5672'
DepthItem = 'DepthItem'
TickerItem = 'TickerItem'
TradeItem = 'TradeItem'
KLineDayItem = 'KLineDayItem'
InfoItem = 'InfoItem'
Symbols = 'Symbols'

SOCK_PROXIES = {
"http": "socks5://127.0.0.1:1080",
'https': 'socks5://127.0.0.1:1080'
}


HEADERS = {
"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"
}


class my_mq:

    def __init__(self,exchange,queue,routing_key,rabbitmq_url=rabbitmq_url):
        self.exchange = exchange
        self.queue = queue
        self.routing_key = routing_key
        self.rabbitmq_url = rabbitmq_url
        self.channel = None


    def create_channel(self, exchange='', queue='', routing_key='', type='direct', durable=False):
        while 1:
            try:
                connection = pika.BlockingConnection(pika.URLParameters(self.rabbitmq_url))
                channel = connection.channel()
                channel.exchange_declare(exchange=exchange, exchange_type=type)
                channel.queue_declare(queue=queue, durable=durable)
                channel.queue_bind(exchange=exchange, queue=queue, routing_key=routing_key)
                self.channel = channel
                break
            except:
                print(traceback.print_exc())
                print(rabbitmq_url, 'connect mq error,retry...')
                time.sleep(5)


    def send_message(self,message, routing_key='', exchange='', properties=pika.BasicProperties(delivery_mode=2, content_type='application/json'), mandatory=False):
        retry =3 
        if (not routing_key) or (not exchange):
            routing_key = self.routing_key
            exchange = self.exchange
        while retry:
            try:
                if not self.channel:
                    self.create_channel(self.exchange,self.queue,self.routing_key)
                if mandatory:
                    self.channel.confirm_delivery()
                self.channel.basic_publish(exchange=exchange,
                                      routing_key=routing_key,
                                      body=message,
                                      properties=properties,
                                      mandatory=mandatory,
                                      )
                return True
            except Exception as e:
                print('MQ server error !!!!!',e)
                retry -=1
        return False



class my_format:


    def conver_num_math(self,_in):
        _in = str(_in).replace(',','')
        if 'e' not in _in:
            return _in
        else:
            num = re.search(r'e-\d+',_in)[0]
            _num = int(num.replace('e-',''))
            num_zero = '0.'+ '0'*(_num-1)+_in.replace(num,'').replace('.','')
            return num_zero


    def _Upper(self,word):
        return word.upper()

    def get_unit(self,price, price_decimal=None):
        price = self.conver_num_math(price)
        if math.modf(float(price))[0] != 0:
            if price_decimal is None:
                return '0.' + '1'.zfill(len(self.conver_num_math(price).split('.')[-1]))
        return '1'


    def format_symbols(self,exchange_id,symbols,exchange_name):
        if not isinstance(symbols,list):
            print('bad symbols !!! error 001')
            return
        return json.dumps({"exchange_id": exchange_id, "symbols": symbols, "item_type": "Symbols_"+exchange_name})


    def format_tick(self,exchange_name,subject,exchange_id,price,unit,ts):
        price =self.conver_num_math(price)
        return json.dumps({"item_type": "TickerItem_"+exchange_name, "subject": subject, "exchange_id": exchange_id, "price": price, "unit": unit, "ts": ts})


    def get_13_str_time(self,t=None):
        if not t:
            t = time.time()
        if not isinstance(t,str):
            t = str(t)
        t = t.replace('.','')
        if len(t) > 13:
            return t[:13]
        elif len(t) == 13:
            return t
        else:
            while len(t) < 13:
                t += '0'
            return t




class my_websocket:


    def on_error(self,ws, error):
        print(error)

    
    def on_close(self):    
        print("### closed ###")


    def get_a_ws(self,url,on_message,message,cookies={},proxies={}):
        self.ws = websocket.WebSocketApp(url,
                                  cookie=cookies,
                                  on_message = on_message,
                                  on_error = self.on_error,
                                  on_close = self.on_close,
                                  )
        self.message = message
        return True


    def send_message(self):
        print(self.message,'---')
        try:
            if isinstance(self.message,str):
                self.ws.send(self.message)
            else:
                for mess in self.message:
                    self.ws.send(mess)
            return True
        except:
            return False


    def run(self,inter=60,timeout=59):
        self.ws.on_open = self.send_message
        self.ws.run_forever(ping_interval=inter,ping_timeout=timeout)



    def run_always(self,inter=60,timeout=59):
        self.ws.on_open = self.send_message
        while  1:
            self.ws.run_forever(ping_interval=inter,ping_timeout=timeout)






def count_time(func):
    def int_time(*args, **kwargs):
        start_time = time.time()  
        res = func(*args, **kwargs)
        over_time = time.time()   
        total_time = (over_time-start_time)
        print('》》》》》',traceback.extract_stack()[-2][0].split('/')[-1],'》》》》》》》》》》》》》 download 用时 %s 秒  \n' % total_time)
        return res
    return int_time




TIMEOUT = 4
@count_time
def json_download(url,method='get',data={},params={},headers={},cookies={},proxies={},retry=3,verify=False,timeout=TIMEOUT):

    while  retry:
        try:
            if method == 'post':
                r = requests.post(url,data=data,headers=headers,cookies=cookies,timeout=timeout,proxies=proxies,verify=verify)
                if r.status_code==200:
                    res = json.loads(r.text)
                else:
                    raise Exception('post request error !!')
            else:
                r = requests.get(url,params=params,headers=headers,cookies=cookies,timeout=timeout,proxies=proxies,verify=verify)
                if r.status_code==200:
                    res = json.loads(r.text)
                else:
                    raise Exception('get request error !!')
            if isinstance(res,dict) or isinstance(res,list):
                return res
            else:
                raise Exception('response not dict error !!')
        except Exception as e:
            print(e)
            retry -= 1


@count_time
def html_download(url,method='get',data={},params={},headers={},cookies={},proxies={},retry=3,verify=False,timeout=TIMEOUT):

    while  retry:
        try:
            if method == 'post':
                r = requests.post(url,data=data,headers=headers,cookies=cookies,timeout=timeout,proxies=proxies,verify=verify)
                if r.status_code==200:
                    return r.text            
            else:
                r = requests.get(url,params=params,headers=headers,cookies=cookies,timeout=timeout,proxies=proxies,verify=verify)
                if r.status_code==200:
                    return r.text
            raise Exception('status_code error')
        except Exception as e:
            print(e)
            retry -=1








