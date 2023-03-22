class Event:
    class Priority:
        HIGH = 0
        MEDIUM = 1
        LOW = 2

    def __init__(self):
        pass

class FrpcSyncEvent(Event):
    def __init__(self, api_query_result):
        self.api_query_result = api_query_result

class FrpcStartEvent(Event):
    def __init__(self, frpc_daemon):
        self.frpc_daemon = frpc_daemon

class DaemonStartEvent(Event):
    def __init__(self):
        pass

class DaemonStopEvent(Event):
    def __init__(self):
        pass

class FrpcPauseEvent(Event):
    def __init__(self):
        pass

class EventMgr:
    def __init__(self):
        self._handler_list = [{}, {}, {}]

    def registerHandler(self, event: type, handler, priority = Event.Priority.MEDIUM):
        if event in self._handler_list:
            self._handler_list[priority][event].append(handler)
        else:
            self._handler_list[priority][event] = [handler]

    def fire(self, event: Event):
        for _p_handler_list in self._handler_list:
            if type(event) in _p_handler_list:
                for handler in _p_handler_list[type(event)]:
                    handler(event)
        return event