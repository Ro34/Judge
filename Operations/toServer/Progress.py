import time

import requests

from Judge import judger
from Judge.Operations.Services_ import MissionInfo
from Judge.Operations.Services_.MissionInfo import add_info, update_info
from Judge.Operations.toPlatform.ReportProgress import report_progress


def progress_trans():
    global row
    missionType = judger.m['missionType']
    platformContext = judger.m['platformContext']
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

        while mission_progress != 0:
            row = add_info(server_pid, missionType, epoch, total_epoch, mission_progress)

        if mission_progress != MissionInfo.mission_list[row][4]:
            update_info(server_pid, mission_progress)

        # progress = res.text.lstrip('[').rstrip(']')
        # print(progress)
        # report_progress(5, 8, progress)
        # 回报进度
        report_progress(platformContext, epoch, total_epoch, mission_progress)
        time.sleep(5)
        if mission_progress == 1:
            break
