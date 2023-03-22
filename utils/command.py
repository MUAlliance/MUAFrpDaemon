class Command:
    class Priority:
        HIGH = 0
        MEDIUM = 1
        LOW = 2

    def __init__(self, name : str, *alias):
        self._name = name
        self._alias = alias

    def match(self, s : str):
        return self._name == s or s in self._alias

    def exec(self, s : list[str], raw : str) -> None:
        pass

class CommandParser:
    def __init__(self):
        self._cmd_list : list[Command] = [[], [], []]

    def register(self, command : Command, priority = Command.Priority.MEDIUM):
        self._cmd_list[priority].append(command)

    def parse(self, cmd_raw : str):
        cmd_l = cmd_raw.strip().split(" ")
        # Priority
        for _list in self._cmd_list:
            for cmd in _list:
                if cmd.match(cmd_l[0]):
                    cmd.exec(cmd_l, cmd_raw)
                    return True
        return False