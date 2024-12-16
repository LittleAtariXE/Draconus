import os
from threading import Lock
from termcolor import cprint
from datetime import datetime

class LocalMessanger:
    def __init__(self, queen_callback: object):
        self.queen = queen_callback
        self.conf = self.queen.conf
        self.log_file_path = os.path.join(self.conf.dir_logs, "Draconus_log.txt")
        self.log_hive_file_path = os.path.join(self.conf.dir_logs, "Hive_log.txt")
        self.lock = Lock()
        self.msg_no_imp = self.conf.show_no_important_messages
        self.msg_dev = self.conf.dev_msg
        self.colors = {
            "msg" : "yellow",
            "no_imp" : "yellow",
            "error" : "red",
            "dev" : "blue"
        }
        self.make_files()

    @property
    def date(self) -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def make_files(self) -> None:
        if not os.path.exists(self.log_hive_file_path):
            with open(self.log_hive_file_path, "w") as file:
                file.write(f"START LOG FILE: {self.date}\n")
                file.write("*" * 80)
                file.write("\n\n")
    
    def add_log_txt(self, msg: str, sender: str) -> None:
        with self.lock:
            with open(self.log_file_path, "a+") as file:
                file.write("-" * 80 + "\n")
                file.write(f"{self.date} [{sender}] {msg}\n")
            with open(self.log_hive_file_path, "a+") as file:
                file.write("-" * 80 + "\n")
                file.write(f"{self.date} [{sender}] {msg}\n")
    
    def show_msg(self, types: str, msg: str, sender: str) -> None:
        color = self.colors[types]
        if types == "no_imp" and not self.msg_no_imp:
            return
        if types == "dev" and not self.msg_dev:
            return
        cprint(f"[{sender}] {msg}", color)
    
    def work(self, types: str, msg: str, sender: str = "Queen"):
        self.add_log_txt(msg, sender)
        self.show_msg(types, msg, sender)
    
    def __call__(self, types: str, msg: str, sender: str = "Queen"):
        self.work(types, msg, sender)
        
