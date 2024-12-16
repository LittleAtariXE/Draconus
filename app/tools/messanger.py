import socket
import json
import os

from datetime import datetime
from threading import Thread, Lock


class Messenger:
    def __init__(self, builder_object: object, name: str, fd_path: str = None):
        self.name = name
        self.config = builder_object
        self.log_file = os.path.join(self.config.dir_logs, f"{name}_log.txt")
        if not fd_path:
            self.fd_path = self.config.socket_draco_msg
        else:
            self.fd_path = fd_path
        self.sep = self.config.unix_socket_separator
        self.is_connected = False
        self.buffer = []
        self.lock = Lock()
        self.conn = None
        self.key_max_len = 30
        self.value_max_len = 80
    
    @property
    def date(self) -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def make_log_file(self) -> None:
        if not os.path.exists(self.log_file):
            with open(self.log_file, "w") as file:
                file.write(f"START LOG FILE: {self.date}\n")
                file.write("*" * 80)
                file.write("\n\n")
    
    def build_socket(self) -> bool:
        try:
            os.unlink(self.fd_path)
        except:
            pass
        try:
            self.server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.server.bind(self.fd_path)
            self.server.listen(1)
            return True
        except OSError as e:
            print("ERROR: ",e)
            return False
    
    def listening(self) -> None:
        while True:
            self.conn, self.addr = self.server.accept()
            self.empty_buffer()
    
    def send_msg(self, types: str, msg: str, sender: str) -> None:
        data = {
            "types" : types,
            "msg" : msg,
            "sender" : sender
        }
        if not self.conn:
            self.buffer.append(data)
            return
        try:
            sdata = json.dumps(data)
            sdata += self.sep
        except json.JSONDecodeError as e:
            print("ERROR: ",e)
            return
        try:
            self.conn.sendall(sdata.encode(self.config.unix_socket_format))
        except (OSError, BrokenPipeError, ConnectionError, ConnectionResetError, ConnectionAbortedError):
            self.buffer.append(data)
    
    def add_log_txt(self, types: str, msg: str, sender: str) -> None:
        with self.lock:
            with open(self.log_file, "a+") as file:
                file.write("-" * 80 + "\n")
                file.write(f"{self.date} [{sender}] {msg}\n")
    
    def start_server(self) -> bool:
        if not self.build_socket():
            return None
        self.th_listening = Thread(target=self.listening, daemon=True)
        self.th_listening.start()
    
    def empty_buffer(self) -> None:
        for m in self.buffer:
            self.send_msg(m["types"], m["msg"], m["sender"])
        self.buffer = []
    
    def split_string(self, text: str, split_len: int) -> list:
        data = []
        for i in range(0, len(text), split_len):
            data.append(text[i:i+split_len])
        fdata = ""
        for i, d in enumerate(data):
            if i == 0:
                fdata += d + "\n"
                continue
            fdata += f"{'':<{self.key_max_len}}{d}\n"
        return fdata


        
    def sort_simple(self, data: dict) -> str:
        max_len = max(len(key) for key in data.keys())
        if max_len > self.key_max_len:
            return str(data)
        text = ""
        for k, v in data.items():
            if len(str(v)) > self.value_max_len:
                v = self.split_string(str(v), self.value_max_len)
            text += f"{k:<{self.key_max_len}}{v}\n"
        return text

    def sorting(self, data: dict, types: str = "simple", name: str = None) -> str:
        if not name:
            name = "\n*********************************************************\n"
        else:
            name = f"\n*********** {name} ************\n"
        data = name + self.sort_simple(data)
        return data


    
    def work(self, types: str, msg: str, sender: str = None, sort: str = None, sort_name: str = None) -> None:
        if sort:
            msg = self.sorting(msg, name=sort_name)
        if not sender:
            sender = self.name
        if types != "dev":
            self.add_log_txt(types, msg, sender)
        self.send_msg(types, msg, sender)
        if self.config.vanilla_print:
            print(f"[{sender}] {msg}")
    
    
    def START(self) -> None:
        self.make_log_file()
        self.start_server()

    
    def __call__(self, types: str, msg: str, sender: str = None, sort: str = None, sort_name: str = None) -> None:
        self.work(types, msg, sender, sort, sort_name)
        

