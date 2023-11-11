import os

from daemon import *

class VelocityAutoUpdater:
    def __init__(self):
        DAEMON.eventMgr.registerHandler(DaemonStartEvent, self.onDaemonInit, Event.Priority.HIGH)

    def onDaemonInit(self, event : DaemonStartEvent) -> None:
        if not os.path.exists(self.__frpc_log_dir):
            os.makedirs(self.__frpc_log_dir)
        self.redirectFrpcLog()
        schedule.every().day.at("00:00:00").do(self.redirectFrpcLog)
        self.__start()