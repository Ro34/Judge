
import time
import requests
import json

import time
   
    
ip = 'http://192.168.9.81:5013'
path = '/AiServer/AcceptMission'
am_url = ip + path
headers = {
            "Content-Type": "application/json"
        }


def cancel_ack():
    cancel_ack_data = {
        'ack' :'mission_cancelled_ok'
        }
    requests.post(url=am_url ,headers=headers ,data=cancel_ack_data)


class accept_mission:

    def request_res(platformContext):
        am_data = {
            'host' :'192.168.9.99'  ,  # 服务器的 IP 或域名
            'port' :60082  ,  # 接受任务的服务端口
            'platformContext' :platformContext  ,  # 平台上下文字段，来自于任务队列中消息携带的 context
            'serverContext' :'服务器消息'  ,  # 服务器上下文字段，之后来自平台的消息都会原封不动携带该字段
        }
        res = requests.post(url=am_url ,headers=headers ,data=json.dumps(am_data))
        return res

    def accept_ack():
        accept_ack_data = {
            'ack' :'mission_accepted_ok'
            }
        requests.post(url=am_url ,headers=headers ,data=accept_ack_data)


def run_accept(platformContext):
    i = 0
    
    res = accept_mission.request_res(platformContext)
    while True:
        print('打印接受任务情况')
        if  res == None:
        # if res.status_code == 400: i+=1
            print(res.status_code)
            print('第'+str(i)+'/3次 请 求未响应')
            res = accept_mission.request_res()
            if i >= 3:
                break
            time.sleep(2)

        elif res.status_code == 400:
            cancel_ack()
            print('mission_cancelled')
            break

        elif res.status_code == 200:
            accept_mission.accept_ack()
            print('mission_accept')
            break

    if res == None:
        print('reject')
