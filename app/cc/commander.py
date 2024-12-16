import socket
import os
import sys

from termcolor import cprint
from threading import Thread, Event
from typing import Union
from time import sleep

from app.hive.queen import Queen
from app.conn.protocols.unix_handler import UnixHandler


class Commander:
    def __init__(self, builder_object: object, only_queen_FLAG: bool = False):
        self.conf = builder_object
        self.format = self.conf.unix_socket_format
        self.raw_len = self.conf.unix_socket_raw_len
        self.separator = self.conf.unix_socket_separator
        self.socket_to = self.conf.unix_sock_to_recive
        self.msg_sock_path = self.conf.socket_draco_msg
        self.ctrl_sock_path = self.conf.socket_draco_ctrl
        self.msg_no_imp = self.conf.show_no_important_messages
        self.msg_dev = self.conf.dev_msg
        self.working_FLAG = Event()
        self.working_FLAG.clear()
        self.Queen = Queen(self.conf)
        self.queen_FLAG = only_queen_FLAG
        self.message_types_colors = {
            "error" : "red",
            "msg" : "green",
            "no_imp" : "green",
            "dev" : "blue" 
        }

    
    def msg_connection(self) -> bool:
        try:
            self.msg_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.msg_sock.connect(self.msg_sock_path)
            self.msg = UnixHandler(self.working_FLAG, self.msg_sock, self.raw_len, self.format, self.separator, self.socket_to)
            return True
        except OSError as e:
            cprint(f"[SYSTEM] [!!] ERROR: {e} [!!]", "red")
            return False
    
    def ctrl_connection(self) -> bool:
        try:
            self.ctrl_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.ctrl_sock.connect(self.ctrl_sock_path)
            self.ctrl = UnixHandler(self.working_FLAG, self.ctrl_sock, self.raw_len, self.format, self.separator, self.socket_to)
            return True
        except OSError as e:
            cprint(f"[SYSTEM] [!!] ERROR Connected to Draconus [!!]\nError: {e}", "red")
            return False
    
    def check_connections(self) -> bool:
        if self.ctrl_connection():
            if self.msg_connection():
                return True
            else:
                return False
        else:
            cprint("[SYSTEM] Propably Draconus not started. Run Draconus first", "red")
            return False
    
    def _recive_msg(self):
        while True:
            data = self.msg.recive_data()
            if not data:
                break
            for d in data:
                self.show_msg(d)
    
    def recive_msg(self) -> None:
        self.msg_th = Thread(target=self._recive_msg, daemon=True)
        self.msg_th.start()
    
    def show_msg(self, msg: dict) -> None:
        if msg["types"] == "no_imp" and not self.msg_no_imp:
            return
        if msg["types"] == "dev" and not self.msg_dev:
            return
        color = self.message_types_colors.get(msg["types"])
        if msg["sender"] == "Draconus" and not msg["types"] == "error":
            color = "blue"
        cprint(f"\n[{msg['sender']}] {msg['msg']}", color)
    
    def send_raw_CMD(self, cmd: dict) -> None:
        self.ctrl.send_data(cmd)
    
    def send_CMD(self, types: str, cmd: str, data: Union[dict, str, list] = None, **kwargs):
        com = {"types" : types, "cmd" : cmd}
        com.update(**kwargs)
        if data:
            com["data"] = data
        self.ctrl.send_data(com)
    
    def recive_data(self) -> Union[str, dict, None]:
        recv = self.ctrl.recive_data()
        return recv
    
    def Start(self) -> bool:
        os.system("clear")
        if self.queen_FLAG:
            self.Queen.Run()
            return True
        self.working_FLAG.set()
        if not self.check_connections():
            cprint("[SYSTEM] [!!] EXIT PROGRAM [!!]", "red")
            return False
        self.recive_msg()
        sleep(0.3)
        self.Queen.Run()
        return True

