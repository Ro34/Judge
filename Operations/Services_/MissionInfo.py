global mission_list

global message
message = {"missionType": 0,
           "platformContext": 0}


def init_list():
    global mission_list
    mission_list = [[]]  # 创建一个空列表

    mission_list[0].append('server_pid')
    mission_list[0].append('mission_type')
    mission_list[0].append('epoch')
    mission_list[0].append('total_epoch')
    mission_list[0].append('progress')


def add_info(server_pid: int, missionType: str, epoch: int, total_epoch: int, progress: float):
    global list_row
    global mission_list
    print(mission_list)
    list_row = len(mission_list)
    mission_list.append([])
    mission_list[list_row].append(server_pid)
    mission_list[list_row].append(missionType)
    mission_list[list_row].append(epoch)
    mission_list[list_row].append(total_epoch)
    mission_list[list_row].append(progress)
    print('打印任务列表')
    print(mission_list)
    return list_row


def update_info(server_pid, new_progress):
    update_row = 0
    for i in range(list_row):
        try:
            p = mission_list[i].index(server_pid)
            print('index: ' + str(i) + ', ' + str(p))
            update_row = i
        except:
            continue
    mission_list[update_row][4] = new_progress


def delete_info(server_pid):
    # 定位任务所在行
    global delete_row
    for i in range(list_row):
        try:
            p = mission_list[i].index(server_pid)
            print('index: ' + str(i) + ', ' + str(p))
            delete_row = i
        except:
            continue
    del mission_list[delete_row]

# taskID='1'
# missionType='AI'
# server_pid=2
# progress=75
# create_list()
# init_list()
# add_info(taskID,missionType,server_pid,progress)
# taskID='2'
# missionType='AI2'
# server_pid=3
# progress=80
# add_info(taskID,missionType,server_pid,progress)
# print(s)
# print('now_list_row:'+str(list_row+1))
# print('任务数'+str(list_row+1))
# delete_info(75)
# print(s)
