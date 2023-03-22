import subprocess
import os
import sys
import json
import datetime
import schedule

from daemon import *
from config import FRPC_DIR

RELOAD_CONFIG_COMMAND = "prox reload"
VELOCITY_DIR = "velocity"
TRUSTED_ENTRIES_FILE = "plugins/proxied-proxy/TrustedEntries.json"
START_COMMAND = "bash start.sh"

class VelocityCommand(Command):
    def __init__(self):
        pass

    def match(self, s : str):
        return True

    def exec(self, s : list[str], raw : str) -> None:
        SERVER.sendCommand(raw)

class Velocity:
    def __init__(self):
        self.__terminate_cmd = "stop"
        self.__frpc_log_dir = os.path.join(FRPC_DIR, "logs")
        self.__frpc_log_file = None
        self.__subprocess = None
        DAEMON.eventMgr.registerHandler(DaemonStartEvent, self.onDaemonInit)
        DAEMON.eventMgr.registerHandler(FrpcSyncEvent, self.onSync)
        DAEMON.eventMgr.registerHandler(DaemonStopEvent, self.onStop)
        DAEMON.commandParser.register(VelocityCommand(), Command.Priority.LOW)

    def onDaemonInit(self, event : DaemonStartEvent) -> None:
        if not os.path.exists(self.__frpc_log_dir):
            os.makedirs(self.__frpc_log_dir)
        self.redirectFrpcLog()
        schedule.every().day.at("00:00:00").do(self.redirectFrpcLog)
        self.__start()

    def onSync(self, event : FrpcSyncEvent) -> None:
        with open(os.path.join(VELOCITY_DIR, TRUSTED_ENTRIES_FILE), 'w') as f:
            f.write(json.dumps(event.api_query_result["entry_list"]))
        self.sendCommand(RELOAD_CONFIG_COMMAND)

    def onStop(self, event : DaemonStopEvent) -> None:
        self.terminate()

    def alive(self) -> bool:
        return self.__subprocess.poll() is None
    
    def poll(self) -> int:
        return self.__subprocess.poll()
    
    def sendCommand(self, cmd : str) -> None:
        self.__subprocess.stdin.write(cmd.encode())
        self.__subprocess.stdin.flush()
    
    def terminate(self) -> None:
        if self.alive():
            if self.__terminate_cmd is not None:
                self.sendCommand(self.__terminate_cmd)
                self.__subprocess.wait(60)
                if self.alive():
                    self.__subprocess.terminate()
                    self.__subprocess.wait()
            else:
                self.__subprocess.terminate()
                self.__subprocess.wait()

    def restart(self) -> None:
        self.terminate()
        self.__start()

    def __start(self) -> None:
        self.__subprocess : subprocess.Popen = subprocess.Popen(START_COMMAND, cwd=VELOCITY_DIR, stdin=subprocess.PIPE, stdout=sys.stdout, stderr=sys.stderr, shell=True)

    def redirectFrpcLog(self) -> None:
        if self.__frpc_log_file is not None:
            self.__frpc_log_file.close()
        self.__frpc_log_file = open(os.path.join(self.__frpc_log_dir, f"{str(datetime.date.today())}.txt"), 'a')
        DAEMON.frpc.setStdout(self.__frpc_log_file)
        DAEMON.frpc.setStderr(self.__frpc_log_file)

SERVER = Velocity()