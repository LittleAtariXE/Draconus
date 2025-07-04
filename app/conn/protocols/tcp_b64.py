import base64
from typing import Union



class TcpB64:
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
        self.conn_FLAG = ["B64_MSG"]

    
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
            data = base64.b64decode(msg)
        except:
            return ""

        return data
    
    def send_data(self, data: dict) -> None:
        try:
            msg = data.get("cmd")
            if not msg:
                return
            msg = base64.b64encode(msg.encode(self.format))
        except:
            return
        try:
            self.conn.sendall(msg)
        except:
            return