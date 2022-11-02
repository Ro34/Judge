from os import kill
import requests


def kill_pid(get_kill_pid):
    ip = 'http://172.18.60.77:60090'
    path = '/datasets/kill_pid'

    sm_url = ip + path

    sm_data = {
        'server_pid': get_kill_pid
    }

    headers = {
        "Content-Type": "application/json"
    }

    res = requests.get(url=sm_url, headers=headers, params=sm_data)
    print("停止服务" + sm_url)
    print(res.text)

if __name__ == "__main__":
    kill_pid()