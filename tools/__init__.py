import re
import time
import json
import pika
import math
import requests
import traceback
import websocket

# clear requests`s ssl3 warning
requests.packages.urllib3.disable_warnings()


# Global rabbit-mq url, use it send message to rabbit mq
rabbitmq_url = 'amqp://guest:123456@127.0.0.1:5672'
# Global rebbit-mq  (exchange-queue-routing_key)  value.
DepthItem = 'DepthItem'
TickerItem = 'TickerItem'
TradeItem = 'TradeItem'
KLineDayItem = 'KLineDayItem'
InfoItem = 'InfoItem'
Symbols = 'Symbols'

# Global socket proxies, use it to across The Great Wall
SOCK_PROXIES = {
"http": "socks5://127.0.0.1:1080",
'https': 'socks5://127.0.0.1:1080'
}


# Global header in http access
HEADERS = {
"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"
}


class my_mq:
    """
    Rabbit mq class ,you can creat an object to declare channel, send message.
    You need to specfy exchange ,queue, routing_key
    """

    def __init__(self,exchange,queue,routing_key,rabbitmq_url=rabbitmq_url):
        self.exchange = exchange
        self.queue = queue
        self.routing_key = routing_key
        self.rabbitmq_url = rabbitmq_url
        self.channel = None


    def create_channel(self, _type='direct', durable=False):
        """
        Create a channel
        1.direct: A queue can bind one routing_key，Messages on switches 
            are sent to queues with the same routing_key.
        2.topic: A queue can bind some routing_key，Messages on switches 
            are sent to queues with the same routing_key.
        3.fanout：Broadcasting，message on exchange will send to every queue.
            If a message is not received by the consumer, it will be discarded.
        durable: If True, made message Persistence in queue.
        """
        while 1:
            try:
                # Connect with url (contain user & pwd) to rabbit-mq server.
                connection = pika.BlockingConnection(pika.URLParameters(self.rabbitmq_url))
                # Create a channel
                channel = connection.channel()
                # Declare a exchange in channel you just created
                channel.exchange_declare(exchange=self.exchange, exchange_type=_type)
                # Declare a queue in channel you just created
                channel.queue_declare(queue=self.queue, durable=durable)
                # Bind the queue you create to the exchange
                channel.queue_bind(exchange=self.exchange, queue=self.queue, routing_key=self.routing_key)
                self.channel = channel
                break
            except:
                print(traceback.print_exc())
                print(rabbitmq_url, 'connect mq error,retry...')
                time.sleep(5)


    def send_message(self,message,properties=pika.BasicProperties(delivery_mode=2, content_type='application/json'), mandatory=False):
        """
        Use the created channel to send message in specified (exchange , queue, routing-key).
        1.message: message send to mq server
        2.properties: Keep producer messages persistent in local file
        3.mandatory: If mandatory is True,when the exchange cannot find a queue 
                    based on its type and routing key,RabbitMQ will calls the 
                    Basic.Return command to back the message to the producer.
                    If mandatory False,the message is discarded directly in this case.
        """
        retry =3 
        while retry:
            try:
                if not self.channel:
                    self.create_channel()
                if mandatory:
                    # Channel confirm model：send successfully return True ,else return False.
                    # If the queue does not exist, message will be dropped and not notify the producer;
                    # if the exchange does not exist, process will report an error;
                    self.channel.confirm_delivery()
                # Send a message contain routing_key in the exchange you just declared.
                self.channel.basic_publish(exchange=self.exchange,
                                      routing_key=self.routing_key,
                                      body=message,
                                      properties=properties,
                                      mandatory=mandatory,
                                      )
                return True
            except Exception as e:
                print('MQ server error !!!!!',e)
                time.sleep(1)
                retry -=1
        return False



class my_format:
    """A class contain some useful script"""

    def conver_num_math(self,_in):
        """
        _in: a number like '1e-10' ,
        convert it to a complete float num, 
        """
        _in = str(_in).replace(',','')
        if 'e' not in _in:
            return _in
        else:
            num = re.search(r'e-\d+',_in)[0]
            _num = int(num.replace('e-',''))
            num_zero = '0.'+ '0'*(_num-1)+_in.replace(num,'').replace('.','')
            return num_zero


    def get_unit(self,price, price_decimal=None):
        """
        Return precision of a number
        """
        price = self.conver_num_math(price)
        if math.modf(float(price))[0] != 0:
            if price_decimal is None:
                return '0.'+'1'.zfill(len(self.conver_num_math(price).split('.')[-1]))
        return '1'


    def format_symbols(self,exchange_id,symbols,exchange_name):
        """
        Retrun a formated symbols-string
        """
        if not isinstance(symbols,list):
            print('bad symbols !!! error 001')
            return
        return json.dumps({"exchange_id": exchange_id,
                           "symbols": symbols,
                            "item_type": "Symbols_"+exchange_name})


    def format_tick(self,exchange_name,subject,exchange_id,price,unit,ts):
        """
        Retrun a formated ticker-string
        """        
        price =self.conver_num_math(price)
        return json.dumps({"item_type": "TickerItem_"+exchange_name,
                           "subject": subject, 
                           "exchange_id": exchange_id, 
                           "price": price,
                           "unit": unit, 
                           "ts": ts})


    def get_13_str_time(self,t=None):
        """
        Retrun a 13-lens timestamp by param 't' 
        if not 't' ,return a 13-lens timestamp now.
        """         
        if not t:
            t = time.time()
        if not isinstance(t,str):
            t = str(t)
        t = t.replace('.','')
        if len(t) > 13:
            return t[:13]
        else:
            while len(t) < 13:
                t += '0'
        return t


    def __conver_to_13stamp(self,t):
        """
        Convert date like "2018-10-17 18:43:03.213" to timestamp.
        As we know time.mktime() can`t convert milliscond,so sad !!
        But this conversion still retain precision of milliscond ~~
        """

        # Check this param
        if not isinstance(t,str):
            t = str(t)

        # Get nums behind dot 
        try:
            num_behind_point = re.findall(r'\.(\d+)',t)[0]
            if len(num_behind_point) ==1:
                num_behind_point = num_behind_point + '00'
            elif len(num_behind_point) ==2:
                num_behind_point = num_behind_point + '0'
            elif len(num_behind_point)>2:
                num_behind_point = num_behind_point[:3]
        except:
            num_behind_point = '000'

        # Convert time tuple to timestamp
        num_list = list(map(lambda x:int(x),re.findall(r'(\d+)',t)))
        time_tuple = tuple(num_list[:6]+[0,0,0])
        timestamp = int(str(int(time.mktime(time_tuple)))[:10] + num_behind_point)        

        return str(timestamp)


    def get_13_str_time_bygmt(self,t,tz=0):
        """
        Convert datetime to timestamp , be sure the datetime is a gmt/utc time.
        Because time.mktime() funcion just can convert a local-datetime to 
        timestamp,but there is a gmt-datetime ,so we need to correction the 
        timestamp (take out timezone) after a convertion.
        param    t : "2018-10-17 T 18:43:03.213"(like this)
                 tz : 8 (an timezone num between [-12 to 12],
                      convert gmt-x-timezone to gmt-0-timezone)
        return a 13-lens timestamp
        """

        # get loc timestamp
        try:
            timestamp = int(self.__conver_to_13stamp(t))
        except:
            print('!!! get an error date string, return timestamp now ~')
            return self.get_13_str_time()              

        # take out timezone in timestamp
        time_zone_h = time.strftime('%z', time.localtime())[:3]
        timestamp = timestamp + (int(time_zone_h) - tz) * 3600 * 1000

        return str(timestamp)


    def get_13_str_time_byloc(self,t):
        """
        Convert datetime to stamp , be sure datetime is your local time.
        Return a 13-lens timestamp
        """       
        try:
            return self.__conver_to_13stamp(t)
        except:
            print('!!! get an error date string, return timestamp now ~')
            return self.get_13_str_time()            





def create_ws(url, header=None, cookie=None):
    """
    Rerurn a short-connected websocket 
    """
    while 1:
        try:
            if header is None:
                ws = create_connection(url,
                                       #http_proxy_host='127.0.0.1',
                                       #http_proxy_port=1080,
                                       sslopt={"cert_reqs": ssl.CERT_NONE}
                                       )
                return ws
            else:
                ws = create_connection(url,
                                       # http_proxy_host='127.0.0.1',
                                       # http_proxy_port=8888,
                                       sslopt={"cert_reqs": ssl.CERT_NONE},
                                       header=header,
                                       cookie=cookie
                                       )
                return ws
        except:
            print(url, 'connect ws error,retry...')
            time.sleep(5)




class my_websocket:
    """
    Long-connected websocket class,use it`s obj to
    Creat websocket,send message,handle receved message etc
    """

    def __on_error(self,ws, error):
        """
        Handle error situation
        """
        print(error)

    
    def __on_close(self):   
        """
        Handle close situation
        """    
        print("### closed ###")


    def get_a_ws(self,url,on_message,message,proxies={}):
        """
        Create a websocket,you need specify :
            url: websocket connect to
            on_message: a func handle received message,
            message: websocket send to server
        """        
        self.ws = websocket.WebSocketApp(url,
                                  on_message = on_message,
                                  on_error = self.__on_error,
                                  on_close = self.__on_close,
                                  )
        self.message = message
        return True


    def send_message(self):
        """
        Send message by created websocket
        """          
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
        """
        Run websocket once
        """          
        self.ws.on_open = self.send_message
        self.ws.run_forever(ping_interval=inter,ping_timeout=timeout)



    def run_always(self,inter=60,timeout=59):
        """
        Run websocket always
        """        
        self.ws.on_open = self.send_message
        while  1:
            self.ws.run_forever(ping_interval=inter,ping_timeout=timeout)




def count_time(func):
    """
    Func wrap , it used to evaluate how long a function takes.
    """
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
    """
    Download func ,return a list or dict object
    """
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
    """
    Download func ,return a html text 
    """
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



