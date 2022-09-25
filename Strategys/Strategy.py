from aliyun_env import *
import json
import os
import shutil
import subprocess
import tempfile
import zipfile
from threading import Timer
import time
import requests
import random
import pika
import sys
sys.path.append("..")

CodeFile = {
    "Pascal": "code.pas",
    "Pascal -O2": "code.pas",
    "C++": "code.cpp",
    "C++ -O2": "code.cpp",
    "C": "code.c",
    "C -O2": "code.c",
    "Java": "Main.java",
    "Python 2.7": "code.py",
    "Python 3.6": "code.py"
}


class Strategy(object):
    def __init__(self, connection, console, error, config, index):
        self.__connection = connection
        self.__console = console
        self.__error = error
        self._config = config
        self._index = int(index) - 1
        self._result = {"result": True, "context": self._config["context"]}

    @staticmethod
    def _readfile(filepath, byte=200):
        fp = open(filepath, 'r')
        ret = fp.read(byte + 1)
        if len(ret) == byte + 1:
            ret = ret[0:byte] + '...'
        fp.close()
        return ret

    def _get_data_file(self, run_path):
        data = {}
        for file_name in os.listdir(run_path):
            if file_name.endswith(".in"):
                data_id = ".".join(file_name.split(".")[:-1])
                out_file_name = data_id + ".out"
                if os.path.exists(os.path.join(run_path, out_file_name)):
                    data[data_id] = [file_name, out_file_name]
        return data

    def _execute(self, run_path, timeout):
        limitMemory = "512m"
        stackLimit = str(128 * 1024 * 1024)
        command = ["docker", "run", "--rm"]
        command.extend(["--net", "none"])
        command.extend(["--memory", limitMemory])
        command.extend(["--ulimit", "stack="+stackLimit])
        command.extend(["--cpuset-cpus", str(self._index)])
        command.extend(["-v", ":".join([run_path, "/root/judge_file"])])
        command.extend(["core", "python3", "core.py",
                        "--dir=/root/judge_file"])
        try:
            # subprocess.check_call(command, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL, timeout=timeout)
            subprocess.check_call(
                command, stderr=subprocess.STDOUT, timeout=timeout)
            # subprocess.check_call(command, timeout=timeout)
        except subprocess.TimeoutExpired as e:
            self._error_console("executing error: " + str(e.__doc__) + str(e))
            self._error_console("output: " + str(e.output.decode()))
            self._result["result"] = False
        except subprocess.CalledProcessError as e:
            self._error_console("executing error: " + str(e.__doc__) + str(e))
            self._error_console("output: " + str(e.output.decode()))
            self._result["result"] = False

    def _init_config_file(self, run_path):
        config = {}
        config["limitTime"] = self._config["limitTime"]
        config["limitMemory"] = self._config["limitMemory"]
        config["data"] = self._get_data_file(run_path)
        config["language"] = self._config["language"]
        if "inputFileName" in self._config:
            if self._config["inputFileName"] != "" and self._config["inputFileName"] != None:
                config["inputFileName"] = self._config["inputFileName"]
        if "outputFileName" in self._config:
            if self._config["outputFileName"] != "" and self._config["outputFileName"] != None:
                config["outputFileName"] = self._config["outputFileName"]
        if "validatorUrl" in self._config:
            config["judge"] = self._config["validatorUrl"].split('/')[-1]
        filename = os.path.join(run_path, "config.json")
        json.dump(config, open(filename, 'w'))
        return config

    def _download_file(self, url, filename=None):
        if filename == None:
            filename = url.split('/')[-1].split('?')[0]
        if not os.path.exists('data'):
            os.mkdir('data')
        filename = os.path.join('data/', filename)
        downloading = '.'.join([filename, 'downloading'])
        self._console(' '.join(["downloading file", filename]))
        while True:
            if os.path.exists(filename):
                return filename
            try:
                flag = False
                with open(downloading, "xb") as f:
                    tries = 3
                    while tries > 0:
                        try:
                            tries -= 1
                            data = requests.get(url, stream=True, timeout=20)
                            for chunk in data.iter_content(chunk_size=1024):
                                if chunk:
                                    f.write(chunk)
                            flag = True
                            break
                        except Exception as e:
                            self._error_console("downloading file: " + str(e.__doc__) + str(
                                e) + " remaining " + str(tries) + " time(s) try.")
                if flag:
                    try:
                        os.rename(downloading, filename)
                    except:
                        pass
                else:
                    self._error_console(
                        " ".join(["downloading", filename, "error"]))
                    self._result["result"] = False
                    os.remove(downloading)
            except:
                t = random.uniform(0.5, 1.0)
                self._console(
                    " ".join([filename, "is downloading. retry in ", str(t), "seconds"]))
                time.sleep(t)

    def _mkdtemp(self):
        return tempfile.mkdtemp(suffix=self._config["token"], prefix="judger")

    def _copy_files(self, tmpdir):
        for times in range(3):
            input_file = self._download_file(self._config["inputFileUrl"])
            output_file = self._download_file(self._config["outputFileUrl"])
            try:
                if input_file != None and output_file != None:
                    shutil.copy(input_file, tmpdir)
                    shutil.copy(output_file, tmpdir)
                    return
            except Exception as e:
                self._error_console(' '.join(
                    ["error file:", str(e.__doc__), str(e), "try again..." if times < 2 else ""]))
                if os.path.exists(input_file):
                    os.remove(input_file)
                if os.path.exists(output_file):
                    os.remove(output_file)
        self._error_console("error data file")
        self._result["result"] = False

    def _clean_tmp(self, tmpdir):
        shutil.rmtree(tmpdir)

    def _consume(self, run_path):
        raise NotImplementedError

    def _console(self, message):
        self.__console(message)

    def _error_console(self, message):
        self.__error(message)

    def _save_code(self, tmpdir, filename):
        try:
            open(os.path.join(tmpdir, filename), 'w',
                 encoding="utf8").write(self._config["code"])
        except Exception as e:
            self._error_console("Cannot save code: " + str(e.__doc__) + str(e))
            self._result["result"] = False

    def process(self):
        try:
            tmpdir = self._mkdtemp()
            self._copy_files(tmpdir)
            self._save_code(tmpdir, CodeFile.get(self._config["language"]))
            if self._result["result"]:
                self._console('Judge started.')
                self._consume(tmpdir)
            self._clean_tmp(tmpdir)
        except Exception as e:
            self._error_console("Unknown Error: " + str(e.__doc__) + str(e))
            self._result["result"] = False
        self.__send_report()
        self.__console('Judge end.')

    def __send_report(self, retry_time=5, try_times=3):
        tries = 0
        if not self._result["result"]:
            self._error_console(json.dumps(self._config))
        self._result["token"] = self._config["token"]
        while tries < try_times:
            try:
                tries += 1
                connection = pika.BlockingConnection(pika.ConnectionParameters(
                    host=MQHost,
                    port=MQPort,
                    virtual_host=VirtualHost,
                    credentials=pika.PlainCredentials(
                        username=MQUsername,
                        password=MQPassword
                    ),
                    heartbeat_interval=MQHeartBeat
                ))
                channel = connection.channel()
                channel.queue_declare(queue=self._config["callbackQueueName"], durable=True, arguments={
                                      "x-max-priority": 10})
                channel.basic_publish(
                    exchange='',
                    routing_key=self._config["callbackQueueName"],
                    body=json.dumps(self._result),
                    properties=pika.BasicProperties(delivery_mode=2)
                )
                connection.close()
                self._console("report sended.")
                break
            except Exception as e:
                self._console(str(e.__doc__) + str(e))
                self._console(
                    "failed to send report, retried in {} second(s).".format(retry_time))
                time.sleep(retry_time)
