
from os import kill
import requests


def kill_pid(get_kill_pid):
    ip = 'http://192.168.9.99:60082'
    path = '/datasets/kill_pid'

    sm_url = ip + path

    sm_data = {
        'server_pid': get_kill_pid
    }
    
    headers = {
        "Content-Type": "application/json"
    }


    res = requests.get(url=sm_url,headers=headers,params=sm_data)
    print("停止服务"+sm_url)
    print(res.text)