import os
import socket
import textwrap
import json

from datetime import datetime
from threading import Thread, Lock
from typing import Optional


class Messenger:
    def __init__(self, conf: dict, tasker : object = None):
        self.Tasker = tasker
        self.name = conf.get("NAME")
        self.format = conf.get("UNIX_SOCKET_FORMAT", "utf-8")
        self.raw_len = conf.get("UNIX_RAW_LEN", 2048)
        self._main_dir = os.path.dirname(__file__)
        self.socks_dir = conf.get("UNIX_SOCKETS_DIR", os.path.join(self._main_dir, "_sockets"))
        self.sock_file = os.path.join(self.socks_dir, f"{self.name}_msg")
        self.logs_dir = conf.get("OUTPUT_DIR", os.path.join(self._main_dir, "output"))
        self.log_file = os.path.join(self.logs_dir, f"{self.name}.txt")
        self.json_file = os.path.join(self.logs_dir, f"{self.name}.json")
        self.dev = conf.get("MSG_DEV", False)
        self.vanila_print = conf.get("MSG_VANILA_PRINT", False)
        self.no_important = conf.get("MSG_NO_IMPORTANT", False)
        self.log_json = conf.get("MSG_JSON", True)
        self._unpack_space = 45
        self.lock = Lock()
        self.ID = None
        self.jsonLogs = None
        self.server = None
        self.conn = None
        self.addr = None
        self.buff = []
        self.tmp = ""
        self.methods = []
        self.make_file()
        
    
    def collectMethod(self):
        if self.vanila_print:
            self.methods.append(self.vanilaPrint)
        if self.log_json:
            self.methods.append(self.addJsonLog)
        if len(self.methods) == 0:
            self.methods.append(self.emptyMethod)
    
    def emptyMethod(self, *args):
        pass

    def make_file(self):
        if not os.path.exists(self.socks_dir):
            os.mkdir(self.socks_dir)
        if os.path.exists(self.sock_file):
            try:
                os.unlink(self.sock_file)
            except OSError as e:
                print("ERROR: ", e)
                return None
        if not os.path.exists(self.logs_dir):
            os.mkdir(self.logs_dir)
        if not os.path.exists(self.log_file):
            with open(self.log_file, "w") as f:
                f.write(f' ------- {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} -- created log files --------\n\n')
        if not os.path.exists(self.json_file):
            intro = {0 : {"sender": self.name, "msg": f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} created log files'}}
            with open(self.json_file, "w") as f:
                f.write(json.dumps(intro))
    
    def build_socket(self):
        self.server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.server.bind(self.sock_file)
        self.server.listen(1)
    
    def accept_conn(self):
        while True:
            self.conn, self.addr = self.server.accept()
            self.empty_buffer()
    
    def start_server(self):
        self.build_socket()
        self.collectMethod()
        self.loadOldLogs()
        if not self.Tasker:
            acc_conn = Thread(target=self.accept_conn, daemon=True)
            acc_conn.start()
        else:
            self.Tasker.addTask(name="Messenger Task", func_name=self.accept_conn, info="Messenger accept connection task")

    def _send_msg(self, msg: str):
        with self.lock:
            self.conn.send(msg.encode(self.format))
    
    def send_msg(self, sender: str, msg: str, noI: bool = False):
        if noI and self.no_important:
            return
        msg = f"[{self.name}][{sender}] {msg}"
        if not self.conn:
            self.buff.append(msg + "\n")
            return
        try:
            self._send_msg(msg)
        except (OSError, BrokenPipeError, ConnectionAbortedError):
            self.buff.append(msg)
    
    def empty_buffer(self):
        # msg = f"\n -------------- New Logs from {self.name} ------------------\n" + "\n".join(self.buff)
        msg = "".join(self.buff)
        self._send_msg(msg)
        self.buff = []
    
    def loadOldLogs(self):
        with open(self.json_file, "r") as f:
            self.jsonLogs = json.loads(f.read())
        self.ID = len(self.jsonLogs.keys()) - 1

    def addJsonLog(self, sender_ip: str, msg: str, noI: Optional[bool] = False):
        if sender_ip == "":
            sender_ip = self.name
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.lock:
            self.ID += 1
            log = {self.ID : {"sender": sender_ip, "msg" : msg, "date": date}}
            self.jsonLogs.update(log)
            with open(self.json_file, "w") as f:
                f.write(json.dumps(self.jsonLogs, indent=1))
    
    def addLog(self, msg: str):
        with self.lock:
            with open(self.log_file, "a") as f:
                f.write(msg)
    
    def preMsg(self, sender: str, msg: str):
        date = f'\n------------------------- {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} -----------------------\n'
        rmsg = date + f"[{sender}] {msg}\n"
        return rmsg
    
    def log2file(self, sender: str, msg: str, noI: Optional[bool] = False):
        msg = self.preMsg(sender, msg)
        self.addLog(msg)
    
    def makeSpace(self, key: str, text: str, space: int):
        text = textwrap.wrap(text, width=self._unpack_space)
        buff = ""
        for i, t in enumerate(text):
            if i == 0:
                buff += f"\n{key.ljust(space)} - {t}"
            else:
                buff += "\n" + "".ljust(space) + f"   {t}"
        return buff

    def _unpackDict(self, data: dict):
        max_len = max(len(str(k)) for k in data.keys())
        msg = ""
        for k, i in data.items():
            msg += self.makeSpace(str(k), str(i), max_len)
        return msg
    
    def unpackDict(self, data: dict, name: str = ""):
        intro = f"\n-----------------{name}--------------------------"
        return intro + self._unpackDict(data)
    
    def vanilaPrint(self, sender: str, msg: str, noI: bool):
        if noI and self.no_important:
            return
        with self.lock:
            print(f"[{self.name}][{sender}] {msg}")
    
    def devMsg(self, sender: str, msg: str, noI: Optional[bool]= False):
        self.send_msg(sender, msg, noI=False)
        self.log2file(sender, msg, noI=False)
        for method in self.methods:
            method(sender, msg, noI)
    
    
    def __call__(self, msg: str, sender: str = "", dictFormat: bool = False, dictName: str = "", noI: bool = False, dev: bool = False, onlyLog=False):
        if dictFormat:
            msg = self.unpackDict(msg, dictName)
        if dev:
            if self.dev:
                self.devMsg(sender, msg, noI=False)
                return
            else:
                return
        if onlyLog:
            self.log2file(sender, msg)
            self.addJsonLog(sender, msg)
            return
        self.send_msg(sender, msg, noI)
        self.log2file(sender, msg, noI)
        for method in self.methods:
            method(sender, msg, noI)
    
    def START(self):
        self.start_server()
        