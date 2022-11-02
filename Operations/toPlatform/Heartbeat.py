import time
import requests
import json
# from tqdm import tqdm


def heart_beat():
    ip = 'http://192.168.9.81:5013'

    service = '/AiServer/Heartbeat'

    hb_url = ip + service

    hb_data = {
        'host': '172.18.60.77',
        'description': '测 试',
        'ftpUsername': '张伟',
        'ftpPassword': '123',
        'version': '1.3'
    }

    headers = {
        "Content-Type": "application/json"
    }

    res = requests.post(url=hb_url, headers=headers, data=json.dumps(hb_data))
    print("发送心跳包" + hb_url)
    print(res.text)


def run_heartbeat():
    while True:
        heart_beat()

        print("等待30s...")
        # for i in tqdm(range(30)):
        #     time.sleep(1)
        # print('\n')
        time.sleep(30)


if __name__ == "__main__":
    run_heartbeat()
