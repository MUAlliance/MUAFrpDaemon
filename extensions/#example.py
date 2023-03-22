from utils.event import *
from utils.main import *

def handler(event):
    INFO("Handler activated!")

def main():
    DAEMON.eventMgr.registerHandler(DaemonStartEvent, handler)
    INFO("Test plugin loaded!")

main()