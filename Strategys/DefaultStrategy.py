import traceback
from .Strategy import Strategy
import subprocess
import os, shutil
import json


class DefaultStrategy(Strategy):
    def __init__(self, connection, console, error, config, index):
        Strategy.__init__(self, connection, console, error, config, index)

    def _format_result(self, run_path):
        try:
            filename = os.path.join(run_path, "result.json")
            result = json.load(open(filename, 'r'))
            if result["result"] == 5:
                raise Exception("judge core dump")
            elif result["result"] == 4: # Compile Errpr
                self._result["compileResult"] = False
                self._result["compileErrorInfo"] = result.get("compileErrorInfo", "")
            else:
                self._result["compileResult"] = True
                self._result["detail"] = result["cases"][0]
        except Exception as e:
            self._result["result"] = False
            self._error_console("Result Error: " + str(e.__doc__) + str(e))

    def _consume(self, run_path):
        try:
            config = self._init_config_file(run_path)
            # docker_timeout = (self._config["limitTime"] / 1000 + 0.2) * len(config["data"]) + 15
            docker_timeout = 60
            self._execute(run_path, timeout = docker_timeout)
            self._format_result(run_path)

        except Exception as e:
            self._error_console("Unknown Error: " + str(e.__doc__) + str(e))            
            self._result["result"] = False
