# import time

import requests
import json


# from API import progress_paras
# from tqdm import tqdm
# import time, random

# 参数mission_epoch,progress

def report_progress(m, epoch, total_epoch, progress):
    ip = 'http://192.168.9.81:5013'

    path = '/AiServer/ReportProgress'

    rp_url = ip + path

    rp_data = {
        "progressText": "训练轮数(" + str(epoch) + "/" + str(total_epoch) + ")",
        "progress": progress*100,
        "platformContext": m

    }

    headers = {
        "Content-Type": "application/json"
    }

    res = requests.post(url=rp_url, headers=headers, data=json.dumps(rp_data))

    print("回报任务进度")
    print("回报响应" + res.text)
    print("回报响应状态码" + str(res.status_code))
