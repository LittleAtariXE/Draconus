import json
from typing import Union
from app.chameleon.chameleon import Chameleon


class TcpHandler:
    def __init__(
        self,
        working_FLAG: object,
        handler_conn_FLAG: object,
        connection_object: object,
        raw_len: int,
        format_code : str,
        separator : str,
        socket_timeout: int
    ):
        self.working_FLAG = working_FLAG
        self.handler_FLAG = handler_conn_FLAG
        self.conn = connection_object
        self.raw_len = raw_len
        self.format = format_code
        self.separator = separator
        self.socket_timeout = socket_timeout
        self.conn.settimeout(self.socket_timeout)
        self.cham = Chameleon(self.format)
        self.conn_FLAG = ["EXEC_CMD"]
        # self.exec_cmd_FLAG = True
        # self.no_msg_FLAG = False


    def unpack_data(self, data: str) -> list:
        dirty = []
        for d in data.split(self.separator):
            if d == "" or d == " ":
                continue
            dirty.append(d)
        clean = []
        for di in dirty:
            try:
                di = json.loads(di)
                clean.append(di)
            except json.JSONDecodeError as e:
                continue
        
        return clean
    
    def recive_data(self) -> Union[list, None]:
        msg = b""
        while self.working_FLAG.is_set() and self.handler_FLAG.is_set():
            try:
                recv = self.conn.recv(self.raw_len)
            except TimeoutError:
                continue
            except (OSError, ConnectionError, ConnectionAbortedError, ConnectionResetError, ConnectionRefusedError):
                return None
            if recv:
                if len(recv) < self.raw_len:
                    msg += recv
                    break
                else:
                    msg += recv
            else:
                return None
        if msg == b"":
            return None
        try:
            data = self.cham.decrypt(msg)
        except:
            return []

        return self.unpack_data(data)
    
    def send_data(self, data: dict) -> None:
        try:
            data = json.dumps(data)
            data += self.separator
        except json.JSONDecodeError as e:
            return
        try:
            data = self.cham.encrypt(data)
        except:
            return
        try:
            self.conn.sendall(data)
        except:
            return