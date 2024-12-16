import os
import socket
from typing import Union
from threading import Thread
from random import randint


class Sender(Thread):
    def __init__(self, draconus: object, handler: object):
        super().__init__(daemon=True)
        self.draco = draconus
        self.dir_in = self.draco.config.dir_in
        self.ip = self.draco.config.ip
        self.port = None
        self.msg = self.draco.msg
        self.handler = handler
        self.trying_number = 100
        self.socket_to = self.draco.config.sender_socket_to
        self.file_name = None
    
    def check_file(self) -> Union[tuple, None]:
        fpath = os.path.join(self.dir_in, self.file_name)
        if not os.path.exists(fpath):
            self.msg("error", f"[!!] ERROR: File: '{self.file_name}' does not exists in 'IN' directory")
            return None
        flen = os.stat(fpath).st_size
        return (fpath, self.file_name, flen)
    
    def port_allocation(self) -> bool:
        c = 0
        while c < self.trying_number:
            port = randint(20000, 60000)
            try:
                self.server.bind((self.ip, port))
                self.server.listen()
                self.port = port
                return True
            except:
                c += 1
                continue
        self.msg("error", "[!!] No free port found for the server [!!]")
        return False

    
    def build(self) -> bool:
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except Exception as e:
            self.msg("error", f"[!!] ERROR: build Sender Socket: {e} [!!]")
            return False
        if not self.port_allocation():
            return False
        self.msg("no-imp", f"Sender Server '{self.ip}:{self.port}' build successfull. Ready to send files.")
        return True
    
    def set_params(self, file_name: str):
        self.file_name = file_name
    
    def send_msg(self, fname: str, flen: int) -> None:
        msg = {"cmd" : "down", "fname" : fname, "flen" : flen, "port" : self.port}
        self.handler.send_msg(msg)

    
    def work(self) -> None:
        file = self.check_file()
        if not file:
            return
        fpath = file[0]
        fname = file[1]
        flen = file[2]
        self.send_msg(fname, flen)
        self.server.settimeout(self.socket_to)
        try:
            conn, addr = self.server.accept()
        except TimeoutError:
            self.msg("error", "[!!] Sender Socket timeout. Close server. [!!]")
            return
        except (ConnectionAbortedError, ConnectionError, ConnectionResetError):
            self.msg("error", f"[!!] Client: {self.handler.client} close connection")
            return
        try:
            with open(fpath, "rb") as file:
                conn.sendfile(file, 0)
        except Exception as e:
            self.msg("error", f"[!!] ERROR Send File to client: {self.handler.client} : {e} [!!]")
            return
        self.msg("msg", f"Send file: '{fname}' successfull", sender=self.handler.client)
    
    def run(self) -> None:
        if not self.build():
            return
        self.work()


        

