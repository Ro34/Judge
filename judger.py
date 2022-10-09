from multiprocessing import Queue
import requests
import pika
import os
import json
import time
import logging
import logging.config

from Judge.Operations.Services_ import MissionInfo
from Judge.aliyun_env import *

from Judge.Operations.toPlatform.ReportProgress import report_progress
from Judge.Operations.toPlatform import AcceptMission
from Judge.Operations.Services_.MissionInfo import *
from Judge.Operations.interface import progressAPI

global m



# import sys

# sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


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
    global m
    m = eval(body)
    MissionInfo.message = m
    missionType = m['missionType']
    platformContext = m['platformContext']

    print('打印任务参数')
    print(m)
    print('打印任务类型')
    print(m['missionType'])
    if missionType == 'AiModelTraining':
        AcceptMission.run_accept(platformContext)
        channel.basic_ack(delivery_tag=method.delivery_tag)

        # url = "http://192.168.9.99:6080/mmdetection/mmdet_model_train?"

        # datas = []
        # message_dict = json.loads(body)
        # for k, v in message_dict.items():
        #     if k == 'missionType':
        #         continue
        #     else:
        #         if type(v) == str:
        #             v_new = v.replace('/', '%2F')
        #             datas.append(f'{k}={v_new}')
        # para = '&'.join(datas)
        # # print(para)
        # params = m
        # url += para
        # print(url)
        # res = requests.get(url=url, params=params)
        # print('获取进度')
        # # print(res.text)
        # # server_pid = res.json()['process_id']
        # # print(server_pid)
        #
        # 获取进度
        # 需要判断任务启动成功
        time.sleep(20)
        while True:
            res = requests.get(url='http://172.18.60.173:8006/progress/get_progress')
            # if res.status_code == 200:
            #     break
            print(res)
            server_pid = res.json()[3]
            # if res.json()[1]==None:
            mission_progress = res.json()[0]
            total_epoch = max(res.json()[1], res.json()[2])
            epoch = min(res.json()[1], res.json()[2])

            # create_list()
            init_list()
            add_info(server_pid, missionType, epoch, total_epoch, mission_progress)
            # report_progress(5, 8, progress)
            # 回报进度
            report_progress(platformContext, epoch, total_epoch, mission_progress)
            time.sleep(5)
            if mission_progress == 1:
                break


def ErrorConsumer(channel, method, properites, body):
    TaskEnded(method)
    channel.stop_consuming()


def MQConnector():
    return ConnectRabbitMQ(host=MQHost, port=MQPort, virtualHost=VirtualHost, username=MQUsername, password=MQPassword,
                           heartbeat=MQHeartBeat)


def run_judger():
    global rabbitMQChannel
    global rabbitMQConnection
    while True:

        create_list()
        init_list()

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


if __name__ == "__main__":
    # res = requests.get(url='http://172.18.60.173:8006/progress/get_progress')
    # # if res.status_code == 200:
    # #     break
    # print(res)
    # missionType = "aaa"
    # server_pid = res.json()[0]
    # # if res.json()[1]==None:
    # print(server_pid)
    # mission_progress = res.json()[1]
    # print(mission_progress)
    # epoch = res.json()[2]
    # print(epoch)
    # total_epoch = res.json()[3]
    # print(total_epoch)
    # # progress = res.text.lstrip('[').rstrip(']')
    # # print(progress)
    # create_list()
    #
    # init_list()
    # add_info(server_pid, missionType, epoch, total_epoch, mission_progress)
    # # report_progress(5, 8, progress)
    # # 回报进度
    # report_progress("platformContext", epoch, total_epoch, mission_progress)
    # time.sleep(5)
    run_judger()
