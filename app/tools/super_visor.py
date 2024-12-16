
from threading import Thread, Lock
from time import sleep


class MyTask:
    def __init__(self, name: str, th: object, info: str = "", types: str = "system"):
        self.name = name
        self.th = th
        self.types = types
        self.info = info
    
    def show(self) -> str:
        move = 20
        text = f"------ Thread: {self.name} -------\n"
        text += f"{'Name':<{move}}{self.name}\n"
        text += f"{'Types':<{move}}{self.types}\n"
        text += f"{'Info':<{move}}{self.info}\n"
        text += f"{'Working':<{move}}{self.th.is_alive()}\n"
        return text

    def working(self) -> bool:
        if self.th.is_alive():
            return True
        else:
            return False


class SuperVisor:
    def __init__(self, draco_callback: object):
        self.draco = draco_callback
        self.pause_clean = self.draco.config.task_pause_clean
        self.threads = {}
        self.lock = Lock()
    
    
    def add_task(self, name: str, func_name: object, args: tuple = (), info: str = "", types: str = "system", is_daemon: bool = True, start: bool = True):
        th = Thread(target=func_name, args=args, daemon=is_daemon)
        task = MyTask(name, th, info, types)
        with self.lock:
            self.threads[name] = task
        if start:
            th.start()
    
    def add_ready_task(self, name: str, th_object: object, info: str = "", types: str = "server"):
        task = MyTask(name, th_object, info, types)
        with self.lock:
            self.threads[name] = task
        
    
    def show_threads(self) -> str:
        text = ""
        for th in self.threads.values():
            text += "\n" + th.show() + "\n"
        return text
    
    def cleaner(self) -> None:
        while self.draco.working_FLAG.is_set():
            too_clean = []
            for k, i in self.threads.items():
                if not i.working():
                    too_clean.append(k)
            with self.lock:
                for c in too_clean:
                    try:
                        del self.threads[c]
                    except KeyError:
                        pass
            sleep(self.pause_clean)
    
    def Start(self) -> None:
        self.add_task("cleaner", self.cleaner, info="Cleaning stopped threads")


    


