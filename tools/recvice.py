import pika
import time
 

Name = 'TickerItem_A_qbtc'

credentials = pika.PlainCredentials('lim', '123456')
connection = pika.BlockingConnection(pika.ConnectionParameters(
 host='127.0.0.1',credentials=credentials))

channel = connection.channel()

channel.exchange_declare(exchange=Name,exchange_type='direct')#指定发送类型
	
result = channel.queue_declare(exclusive=True)
queue_name = result.method.queue

channel.queue_bind(exchange=Name,queue=queue_name,routing_key=Name)  #随机生成的Q，绑定到exchange上面。

print(' [*] Waiting for logs. To exit press CTRL+C')

def callback(ch, method, properties, body):
    print(body)
    ch.basic_ack(delivery_tag = method.delivery_tag)


channel.basic_consume(callback,
                   queue=queue_name,
                   no_ack=True
                   )
channel.start_consuming()