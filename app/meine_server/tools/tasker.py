import threading

from threading import Thread
from typing import Callable


class MyTask:
    def __init__(self, name: str, th: Thread, func_name: Callable, args=None, info: str = "", types: str ="system", cliID: str = None):
        self.name = name
        self.th = th
        self.func_name = func_name
        self.args = args
        self.info = info
        self.types = types
        self.cliID = cliID
    
    def show(self) -> str:
        buff = f"\n--------------{self.name}------------------\n"
        buff += self.add_line("name", self.name)
        buff += self.add_line("info", self.info)
        buff += self.add_line("types", self.types)
        buff += self.add_line("is_alive", self.th.is_alive())
        buff += self.add_line("raw_th", self.th)
        buff += self.add_line("no_ident", self.th.ident)
        return buff

    
    def add_line(self, key, value) -> str:
        line = f"--- {str(key).ljust(13)}\t--{value}\n"
        return line

class Tasker:
    def __init__(self, server_callback : object):
        self.server = server_callback
        self.Msg = None
        self.tasks = {"system" : [], "handlers" : []}
        self.checking()
    
    def _update(self):
        self.Msg = self.server.Msg
    
    def _rawThread(self) -> list:
        return threading.enumerate()
    
    def addTask(self, name : str, func_name : Callable, args : tuple = (), info : str = "", types : str = "system", cliID : str = None, is_daemon : bool = True, start_now : bool = True):
        th = Thread(target=func_name, args=args, daemon=is_daemon)
        task = MyTask(name, th, func_name, args, info, types, cliID)
        self.tasks[types].append(task)
        if start_now:
            th.start()
    
    def cleaner(self) -> None:
        for types in self.tasks.keys():
            for task in self.tasks[types][:]:
                if not task.th.is_alive():
                    self.tasks[types].remove(task)
    
    def checking(self) -> None:
        for task in threading.enumerate():
            if task.name == "MainThread":
                main = MyTask(name="MainThread", th=task, func_name=None, info="Main Process Thread")
                self.tasks["system"].append(main)

    
    def showTask(self) -> None:
        print(threading.enumerate())
        buff = "\n"
        for k, i in self.tasks.items():
            for x in i:
                buff += x.show()
        self.Msg(buff)


