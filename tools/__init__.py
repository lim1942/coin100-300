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
    Rabbit mq class ,you can creat an object to create channel, send message.
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
        1.direct模式: 根据 exchange发送时的routing_key 和queue的routing_key 判定应该将数据发送至指定队列。
        2.topic模式: 可以让队列绑定几个模糊的关键字，之后发送者将数据发送到exchange，exchange将传入”路由值“和 ”关键字“进行匹配，匹配成功，则将数据发送到指定队列。
        3.fanout：广播类型，exchage将消息发送给所有queue，如果某个消费者没有收到当前消息，就再也收不到了
        durable: 让队列queue中的消息持久化
        """
        while 1:
            try:
                # url密码的形式链接服务器
                connection = pika.BlockingConnection(pika.URLParameters(self.rabbitmq_url))
                # 创建一个channel
                channel = connection.channel()
                # 在channel上申明exchange
                channel.exchange_declare(exchange=self.exchange, exchange_type=_type)
                # 在channel上申明queue
                channel.queue_declare(queue=self.queue, durable=durable)
                # 把申明的queue绑定到exchange上
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
        1.message: 待发送的消息
        2.properties: 使生产者的消息或任务持久化存储
        3.mandatory: 当mandatory参数设为true时，交换器无法根据自身的类型和路由键找到一个符合条件的队列，
                    那么RabbitMQ会调用Basic.Return命令将消息返回给生产者。当mandatory参数设置为
                    false时，出现上述情形，则消息直接被丢弃。
        """
        retry =3 
        while retry:
            try:
                if not self.channel:
                    self.create_channel()
                if mandatory:
                    # exchange的confirm模式：投递失败会返回False，成功返回True，如果队列不存在，
                    # 交换机会叫消息丢掉，但不会通知生产者；如果交换机不存在，会报错；
                    self.channel.confirm_delivery()
                # 在上面申明的exchangge上，指定routing_key发送消息,会把消息发到匹配的queue上
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
        Get a number like '1e-10' ,
        convert it to a complete float num,
        And then return the float num. 
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
        Return precision of an number
        """
        price = self.conver_num_math(price)
        if math.modf(float(price))[0] != 0:
            if price_decimal is None:
                return '0.' + '1'.zfill(len(self.conver_num_math(price).split('.')[-1]))
        return '1'


    def format_symbols(self,exchange_id,symbols,exchange_name):
        """
        Retrun a format symbols string
        """
        if not isinstance(symbols,list):
            print('bad symbols !!! error 001')
            return
        return json.dumps({"exchange_id": exchange_id, "symbols": symbols, "item_type": "Symbols_"+exchange_name})


    def format_tick(self,exchange_name,subject,exchange_id,price,unit,ts):
        """
        Retrun a format ticker string
        """        
        price =self.conver_num_math(price)
        return json.dumps({"item_type": "TickerItem_"+exchange_name, "subject": subject, "exchange_id": exchange_id, "price": price, "unit": unit, "ts": ts})


    def get_13_str_time(self,t=None):
        """
        Retrun a 13 len timestamp by param 't' 
        if not f ,return 13 len timestamp now
        """         
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


    def __conver_to_13stamp(self,t):
        """
        Convert date like "2018-10-17 18:43:03.213" to timestamp.
        As we know time.mktime() can`t convert milliscond,
        But this conversion still retain precision of milliscond ~~
        """

        # onfirm this param
        if not isinstance(t,str):
            t = str(t)

        # get num behind dot 
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

        # convert time tuple to stamp
        num_list = list(map(lambda x:int(x),re.findall(r'(\d+)',t)))
        time_tuple = tuple(num_list[:6]+[0,0,0])
        timestamp = int(str(int(time.mktime(time_tuple)))[:10] + num_behind_point)        

        return str(timestamp)


    def get_13_str_time_bygmt(self,t,tz=0):
        """
        Convert datetime to timestamp , be sure the datetime is a gmt/utc time.
        Because time.mktime() funcion just can convert an local-datetime to 
        timestamp,but there is a gmt-datetime ,so we need to correction the 
        timestamp (take out timezone) after convertion.
        param    t : "2018-10-17 18:43:03.213"(like this)
                 tz : 8 (an timezone num between [-12 to 12],convert gmt-x-timezone to gmt-0-timezone)
        return   a 13-len timestamp
        """

        # get loc timestamp
        try:
            timestamp = int(self.__conver_to_13stamp(t))
        except:
            print('!!! get an error date string, return timestamp now ~')
            return self.get_13_str_time()              

        # take out timezone in timestamp
        time_zone_h = time.strftime('%z', time.localtime())[:3]
        h = int(re.findall(r'(\d+)',time_zone_h)[0])
        ss = h * 3600 * 1000
        if '+' in time_zone_h:
            timestamp = timestamp + ss
        elif '-' in time_zone_h:
            timestamp = timestamp - ss

        # handle specify timezone num
        timestamp = timestamp - tz * 3600 * 1000

        return str(timestamp)


    def get_13_str_time_byloc(self,t):
        """
        Convert datetime to stamp , be sure datetime is your local time.
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
    creat websocket,send message,handle receved message etc
    """

    def __on_error(self,ws, error):
        """
        handle error situation
        """
        print(error)

    
    def __on_close(self):   
        """
        handle close situation
        """    
        print("### closed ###")


    def get_a_ws(self,url,on_message,message,proxies={}):
        """
        create a websocket,you need specify :
            url: websocket connect to
            on_message: a func handle received message,
            message: websocket send  to server
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
        send message by created websocket
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
        run websocket once
        """          
        self.ws.on_open = self.send_message
        self.ws.run_forever(ping_interval=inter,ping_timeout=timeout)



    def run_always(self,inter=60,timeout=59):
        """
        run websocket always
        """        
        self.ws.on_open = self.send_message
        while  1:
            self.ws.run_forever(ping_interval=inter,ping_timeout=timeout)




def count_time(func):
    """
    func wrap , used to evaluate how long a function takes.
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
    download func ,return a list or dict object
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
    download func ,return a html text
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



