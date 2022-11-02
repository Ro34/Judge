import time
import requests
import json

import time

ip = 'http://192.168.9.81:5013'
# ip = 'http://139.196.192.142'
path = '/AiServer/AcceptMission'
am_url = ip + path
headers = {
    "Content-Type": "application/json"
}


class accept_mission:

    def request_res(platformContext, host_ip, port, serverContext):
        am_data = {
            # 'host' :'192.168.9.99'  ,  # 服务器的 IP 或域名
            # 'port' :60082  ,  # 接受任务的服务端口
            'host': host_ip,
            'port': port,
            'platformContext': platformContext,  # 平台上下文字段，来自于任务队列中消息携带的 context
            'serverContext': serverContext,  # 服务器上下文字段，之后来自平台的消息都会原封不动携带该字段
        }
        res = requests.post(url=am_url, headers=headers, data=json.dumps(am_data))
        return res

    def accept_ack():
        accept_ack_data = {
            'ack': 'mission_accepted_ok'
        }
        res = requests.post(url=am_url, headers=headers, data=accept_ack_data)

    def cancel_ack():
        cancel_ack_data = {
            'ack': 'mission_cancelled'
        }
        requests.post(url=am_url, headers=headers, data=cancel_ack_data)


def mission_judgment(platformContext, host_ip, port, serverContext):
    i = 0

    res_ac = accept_mission.request_res(platformContext, host_ip, port, serverContext)

    print(res_ac.request.body)

    while True:
        print('打印接受任务情况')
        print(res_ac.status_code)
        if res_ac.status_code != 200:
            # if res.status_code == 400: i+=1

            print('第' + str(i) + '/3次 请 求未响应')
            res_ac = accept_mission.request_res(platformContext, host_ip, port, serverContext)
            i = i+1
            if i >= 3:
                break
            time.sleep(2)

        elif res_ac.status_code == 200:
            # accept_mission.accept_ack()
            print('mission_accept')

            break

        # elif res_ac.status_code == 400:
        #     accept_mission.cancel_ack()
        #     print('mission_cancelled')
        #     break

    if res_ac is None:
        print('reject')
