from base64 import encode
import encodings
import requests
from Strategys.DefaultStrategy import DefaultStrategy

import pika
import sys
import datetime
import json
import time
import logging
import logging.config
from aliyun_env import *


# logging.config.fileConfig("logger.conf")


def Console(message):
    logger = logging.getLogger("infoLogger")

    logger.info("[{0}] {1}".format(Judgername, message))



def ErrorConsole(message):
    logger = logging.getLogger("errorLogger")

    logger.error("[{0}] {1}".format(Judgername, message))


def ConnectRabbitMQ(host, port, virtualHost, username, password, heartbeat):
    Console('connecting RabbitMQ(host={}, port={}, virtualHost={}, user={}, heartbeat={})'.format(
        host, port, virtualHost, username, heartbeat))
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='192.168.9.82',
        port=5672,
        virtual_host=virtualHost,
        credentials=pika.PlainCredentials(
            username='yijiahe',
            password='yjh@123'
        ),
        heartbeat=heartbeat
    ))
    Console('RabbitMQ connected.')
    return connection


def GetRabbitMQChannel(connection, queue_name, consumer):
    Console('creating RabbitMQ.Channel(queue={})'.format(queue_name))
    channel = connection.channel()
    channel.queue_declare(queue=queue_name, durable=True,
                          arguments={"x-max-priority": 10})
    channel.basic_qos(prefetch_count=30)
    channel.basic_consume(queue=queue_name, consumer_callback=consumer, no_ack=False)
    Console('channel created.')

    return channel


def TaskEnded(method):
    global rabbitMQChannel
    global rabbitMQConnection
    # Console('telling server the task is processed...')
    while True:
        try:
            if rabbitMQConnection.is_closed or rabbitMQChannel.is_closed:
                raise Exception('closed connection')
            rabbitMQChannel.basic_ack(delivery_tag=method.delivery_tag)
            Console('told.')
            break
        except:
            # traceback.print_exc()
            ErrorConsole(
                'failed to execute channel.basic_ack, trying to recreate channel...')
            while True:
                try:
                    rabbitMQChannel = GetRabbitMQChannel(
                        rabbitMQConnection, MQQueueName, Consumer)
                    break
                except:
                    # traceback.print_exc()
                    ErrorConsole(
                        'failed to recreate channel, trying to reconnect server...')
                    while True:
                        try:
                            rabbitMQConnection = MQConnector()
                            break
                        except:
                            # traceback.print_exc()
                            ErrorConsole(
                                'failed to reconnect server, waiting to reconnect again in 5 second(s)...')
                            time.sleep(5)


def Consumer(channel, method, properites, body):
    '''
    aa = str(body,encoding='utf-8')
    with open('aa.txt', 'w', encoding='utf-8') as f:
        f.write(aa)
        # f.close()
    
    with open('aa.txt', 'r', encoding='utf-8') as f: 
         m = f.read()
    print(m)
    
    if m==('[{"missionType": "AiModelTraining", "platformContext": "123"}]'):
        # mission = m[0]['missionType']
        print('+++++++++++++++++++++++++++',eval(m)[-1])
        mission = eval(m)[-1]['missionType']
        print(mission)

        if mission==('AiModelTraining'):
            print("startService")
    '''
    # # print(str(body,encoding='utf-8'))
    # #print(aa.shape())
    m = eval(body)
    mission = 'AiModelTraining'
    # print(mission)

    # print(eval(body))
    # print(type(m))
    # mission = eval(body)[0]['missionType']
    # taskid = eval(body)[0]['task_id']
    print(m['missionType'])
    print(m)
    # print(body)
    channel.basic_ack(delivery_tag=method.delivery_tag)
    if mission=='AiModelTraining':
        channel.basic_ack(delivery_tag=method.delivery_tag)
    #     #http://172.18.60.159:60080/mmdetection/mmdet_model_train?classes=garbage&data_root=data%2Fgarbage&data_samples_pre_gpu=4&data_test_ann_file=annotations%2Finstances_val2017.json&data_test_img_prefix=val2017&data_train_dataset_ann_file=annotations%2Finstances_train2017.json&data_train_dataset_img_prefix=train2017&data_val_ann_file=annotations%2Finstances_val2017.json&data_val_img_prefix=val2017&gpu_ids=0&max_epochs=100&model_config_id=1&model_save_path=data%2Ftrain&workers_per_gpu=2

        url = "http://172.18.60.159:60080/mmdetection/mmdet_model_train?"
    #     url = 'http://172.18.60.159:50043/queryProgressMsg/'

        datas = []
        message_dict = json.loads(body)
        for k, v in message_dict.items():
            if k=='missionType':
                continue
            else:
                if type(v) == str:
                    v_new = v.replace('/', '%2F')
                    datas.append(f'{k}={v_new}')
        para = '&'.join(datas)
        print(para)
        print(1)
        params = m
        url += para
        print(url)
        res = requests.get(url=url,params=params)
        print(res.text)


def ErrorConsumer(channel, method, properites, body):
    TaskEnded(method)
    channel.stop_consuming()


def MQConnector():
    return ConnectRabbitMQ(host=MQHost, port=MQPort, virtualHost=VirtualHost, username=MQUsername, password=MQPassword,
                           heartbeat=MQHeartBeat)


if __name__ == '__main__':
    # print(sys.argv)
    # if (len(sys.argv) != 2):
    #     print("Usage: python3 judger.py index")
    #     exit(0)
    # Judgername += sys.argv[1]
    global rabbitMQChannel
    global rabbitMQConnection
    while True:

        failed_last_time = False
        try:
            rabbitMQConnection = MQConnector()

            if not failed_last_time:
                rabbitMQChannel = GetRabbitMQChannel(
                    rabbitMQConnection, MQQueueName, Consumer)
                print("GetChannel Successful")

                rabbitMQChannel.start_consuming()


            else:
                rabbitMQChannel = GetRabbitMQChannel(
                    rabbitMQConnection, MQQueueName, ErrorConsumer)
                rabbitMQChannel.start_consuming()
                rabbitMQChannel = GetRabbitMQChannel(
                    rabbitMQConnection, MQQueueName, Consumer)
                rabbitMQChannel.start_consuming()
                failed_last_time = False

        except Exception as e:
            failed_last_time = True
            ErrorConsole(
                'connection lost, waiting to reconnect in 5 second(s)...')
            print(e)
            time.sleep(5)
