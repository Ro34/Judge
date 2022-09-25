## 概述
本测评机用于为[Aspirin Code](longint.org)提供测评服务

## 配置测评机环境
### 安装必需的系统 (基于Ubuntu16.04)
```
sudo apt update
sudo apt upgrade -y python3
sudo apt install -y git docker.io python3-pip
pip3 install --upgrade requests
pip3 install pika ConcurrentLogHandler
```

### 下载或Clone测评脚本
```
git clone https://github.com/Hzfengsy/Judge-Core.git
```

### 构建Docker镜像
```
cd Judge-Core/
sudo docker build --rm -f Dockerfile -t core:latest .
```
### 配置网络环境
```
cp env_example.py env.py
```
### 配置服务脚本
```
sudo vi /etc/init.d/judger
sudo chmod +x /etc/init.d/judger
sudo update-rc.d judger defaults
```
文件内容如下
```
#!/bin/bash
#
# /etc/init.d/judger -- startup script for Linux-Dash
#
# Written by Hzfengsy
#
### BEGIN INIT INFO
# Provides:          Hzfengsy
# Required-Start:    $remote_fs $network
# Required-Stop:     $local_fs
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Description:       judge service
### END INIT INFO

NAME=judger
DESC="judger"
N=3
path=/root/Judge-Core
start()
{
        cd $path
        rm data/*.downloading
        for ((i=1; i<=$N; ++i))
        do
                echo $i
                nohup python3 judger.py $i >/dev/null 2>&1 &
        done
        echo "judge service started."
}

stop()
{
        kill -9 $(pidof python3 judger)
        echo "judge service stopped."
}
case "$1" in
        start)
                start
                ;;
        stop)
                stop
                ;;
        restart|reload)
                stop
                start
                ;;
        *)
            echo "Usage:" $0 "{start | stop | restart | reload}"
esac
exit 0
```

### 服务管理
```
service judger start           # 运行服务
service judger stop            # 停止服务
service judger restart/reload  # 重启服务
```