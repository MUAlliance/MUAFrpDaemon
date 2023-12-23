import subprocess
import os
import sys
import json
import datetime
import schedule
from utils import extension_config

from daemon import *
from config import FRPC_DIR

class MinecraftProxyCommand(Command):
    def __init__(self):
        pass

    def match(self, s : str):
        return True

    def exec(self, s : list[str], raw : str) -> None:
        SERVER.sendCommand(raw)

class MinecraftProxy:
    def __init__(self):
        self.__terminate_cmd = "stop"
        self.__frpc_log_dir = os.path.join(FRPC_DIR, "logs")
        self.__frpc_log_file = None
        self.__subprocess = None
        self.__config = extension_config.load_config("minecraft.yml", {
            "reload_config_command" : "prox reload",
            "minecraft_proxy_dir" : "server",
            "trusted_entries_file" : "plugins/proxied-proxy/TrustedEntries.json",
            "start_command" : "bash start.sh"
        })
        DAEMON.eventMgr.registerHandler(DaemonStartEvent, self.onDaemonInit)
        DAEMON.eventMgr.registerHandler(FrpcSyncEvent, self.onSync)
        DAEMON.eventMgr.registerHandler(DaemonStopEvent, self.onStop)
        DAEMON.commandParser.register(MinecraftProxyCommand(), Command.Priority.LOW)

    def getDir(self):
        return self.__config["minecraft_proxy_dir"]

    def onDaemonInit(self, event : DaemonStartEvent) -> None:
        if not os.path.exists(self.__frpc_log_dir):
            os.makedirs(self.__frpc_log_dir)
        self.redirectFrpcLog()
        schedule.every().day.at("00:00:00").do(self.redirectFrpcLog)
        self.__start()

    def onSync(self, event : FrpcSyncEvent) -> None:
        fpath = os.path.join(self.__config["minecraft_proxy_dir"], self.__config["trusted_entries_file"])
        fdir = os.path.dirname(fpath)
        if not os.path.exists(fdir):
            os.makedirs(fdir)
        with open(os.path.join(self.__config["minecraft_proxy_dir"], self.__config["trusted_entries_file"]), 'w') as f:
            f.write(json.dumps(event.api_query_result["entry_list"]))
        self.sendCommand(self.__config["reload_config_command"])

    def onStop(self, event : DaemonStopEvent) -> None:
        self.terminate()

    def alive(self) -> bool:
        return self.__subprocess.poll() is None
    
    def poll(self) -> int:
        return self.__subprocess.poll()
    
    def sendCommand(self, cmd : str) -> None:
        if not cmd.endswith(os.linesep):
            cmd += os.linesep
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
        self.__subprocess : subprocess.Popen = subprocess.Popen(self.__config["start_command"], cwd=self.__config["minecraft_proxy_dir"], stdin=subprocess.PIPE, stdout=sys.stdout, stderr=sys.stderr, shell=True)

    def redirectFrpcLog(self) -> None:
        if self.__frpc_log_file is not None:
            self.__frpc_log_file.close()
        self.__frpc_log_file = open(os.path.join(self.__frpc_log_dir, f"{str(datetime.date.today())}.txt"), 'a')
        DAEMON.frpc.setStdout(self.__frpc_log_file)
        DAEMON.frpc.setStderr(self.__frpc_log_file)

SERVER = MinecraftProxy()