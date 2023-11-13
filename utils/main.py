import sys
import os
import subprocess
import threading
import schedule
import traceback
import hashlib
import platform

from config import *
from utils.command import *
from utils.event import *
from utils.union_api import UnionAPI

DAEMON = None
INFO = None
WARN = None


class FrpcDaemon:
    def __init__(self):
        self.__frpc_servers = {}
        self.__frpc_threads : dict[str : subprocess.Popen] = {}
        self.__lock = threading.Lock()
        self.__job = None
        self.__stdout = sys.stdout
        self.__stderr = sys.stderr
        frpc_bin = "frpc"
        if platform.system() == "Windows":
            frpc_bin = "frpc.exe"
        self.__frpc_bin = os.path.join(FRPC_DIR, frpc_bin)
        self.__union_api = UnionAPI(FRPC_UNION_API_NETWORK)

    @property
    def union_api(self) -> UnionAPI:
        return self.__union_api

    def __restartFrpcProcesses(self, configs : list) -> None:
        self.__lock.acquire()
        new_servers = {}
        keep_servers = {}
        delete_servers = []
        for item in configs:
            item_str = item['id'] + str(item['config'])
            item_hash = hashlib.md5(item_str.encode('utf-8')).hexdigest()
            if item_hash not in self.__frpc_servers:
                new_servers[item_hash] = item
            else:
                keep_servers[item_hash] = item
        for item_hash in self.__frpc_servers:
            if item_hash not in keep_servers:
                delete_servers.append(item_hash)
        for new_hash, new in new_servers.items():
            config_fname = os.path.join(FRPC_DIR, f'{new_hash}.toml')
            with open(config_fname, "w") as f:
                config = new['config']
                for placeholder, repl in FRPC_CONFIG_PLACEHOLDERS.items():
                    config = config.replace(f"#{placeholder}#", repl)
                f.write(config)
            self.__frpc_threads[new_hash] = self.__startFrpc(config_fname)
            self.__frpc_servers[new_hash] = new
        for rm_hash in delete_servers:
            self.__frpc_threads[rm_hash].terminate()
            self.__frpc_threads[rm_hash].wait()
            DEBUG(f"{self.__frpc_threads[rm_hash].pid} {self.__frpc_threads[rm_hash].poll()}")
            del self.__frpc_threads[rm_hash]
            del self.__frpc_servers[rm_hash]
            os.remove(os.path.join(FRPC_DIR, f"{rm_hash}.toml"))
        self.__lock.release()

    def __startFrpc(self, config_fname : str) -> subprocess.Popen:
        ret = subprocess.Popen([self.__frpc_bin, "-c", config_fname], shell=False, stdin=subprocess.PIPE, stdout=self.__stdout, stderr=self.__stderr)
        DEBUG(f"Created proc: {ret.pid}")
        return ret
    
    def start(self) -> None:
        self.sync()
        DAEMON.eventMgr.fire(FrpcStartEvent(self))

    def sync(self) -> None:
        response = self.__union_api.queryAPI()
        event = FrpcSyncEvent(self, response)
        DAEMON.eventMgr.fire(event)
        self.__restartFrpcProcesses(event.api_query_result['frpc'])

    def startScheduledTask(self, scd : schedule.Job) -> None:
        if self.__job is None:
            self.__job = scd.do(self.sync)

    def stop(self) -> None:
        schedule.cancel_job(self.__job)
        self.__job = None
        for server_hash, server in self.__frpc_threads.items():
            server.terminate()
            server.wait()
            os.remove(os.path.join(FRPC_DIR, f"{server_hash}.toml"))
    
    def setStdout(self, stdout) -> None:
        self.__stdout = stdout

    def setStderr(self, stderr) -> None:
        self.__stderr = stderr

class Daemon:
    def __init__(self):
        self.__frpc = FrpcDaemon()
        self.__event_mgr = EventMgr()
        self.__command_parser = CommandParser()
        self.__main_thread_semaphore = threading.Semaphore(0)
        self.__stdin = sys.stdin 
        self.__stdout = sys.stdout
        self.__stderr = sys.stderr

    @property
    def frpc(self) -> FrpcDaemon:
        return self.__frpc
    
    @property
    def eventMgr(self) -> EventMgr:
        return self.__event_mgr
    
    @property
    def commandParser(self) -> CommandParser:
        return self.__command_parser

    def daemon(self) -> None:
        try:
            self.info("Starting daemon...")
            self.eventMgr.fire(DaemonStartEvent(self.__frpc))
            self.__frpc.startScheduledTask(FRPC_SYNC_SCHEDULE)
            self.__frpc.start()
            self.commandParser.register(stopCommand())
            self.commandParser.register(ManagerCommand())
            self.info("Frpc started.")
            while(True):
                cmd = self.__stdin.readline()
                if not self.__command_parser.parse(cmd):
                    self.warn("Unknown command!")
        except:
            traceback.print_exc()
            DAEMON.stop()

    def info(self, s : str) -> None:
        self.__stdout.write(f"[INFO] {s}\n")

    def warn(self, s : str) -> None:
        self.__stderr.write(f"[WARN] {s}\n")

    def error(self, s : str) -> None:
        self.__stderr.write(f"[ERROR] {s}\n")

    def debug_none(self, s : str) -> None:
        pass

    def debug(self, s : str) -> None:
        self.__stdout.write(f"[DEBUG] {s}\n")

    def start(self) -> None:
        self.__thread = threading.Thread(target=self.daemon, daemon=True)
        self.__thread.start()
        self.__main_thread_semaphore.acquire()

    def stop(self) -> None:
        try:
            self.info("Shutting down...")
            self.frpc.stop()
            self.__event_mgr.fire(DaemonStopEvent(self.__frpc))
        except :
            traceback.print_exc()
        finally:
            self.__main_thread_semaphore.release()

class ManagerCommand(Command):
    def __init__(self):
        super().__init__("!!union")

    def exec(self, s : list[str], raw : str) -> None:
        if len(s) == 2:
            if s[1] == "reload":
                INFO("Reloading frpc...")
                DAEMON.frpc.sync()

class stopCommand(Command):
    def __init__(self):
        self.stop_command_list = [ "!!stop", "/stop", "stop" ]

    def match(self, s : str) -> bool:
        return s in self.stop_command_list or len(s) == 0 # Ctrl+C

    def exec(self, s : list[str], raw : str) -> None:
        DAEMON.stop()

def greet():
    print("===============================================")
    print("")
    print("    Frpc daemon created by SJMC Cakedreamer    ")
    print("")
    print("===============================================")

DAEMON = Daemon()
INFO = DAEMON.info
WARN = DAEMON.warn
if DEBUG_ENABLED:
    DEBUG = DAEMON.debug
else:
    DEBUG = DAEMON.debug_none