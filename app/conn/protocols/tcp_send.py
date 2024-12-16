from typing import Union

class TcpRawSend:
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
        # *1000 - prevent socket TO error when client recive files
        self.socket_timeout = socket_timeout * 1000
        self.conn.settimeout(self.socket_timeout)
        # self.exec_cmd_FLAG = False
        # self.no_msg_FLAG = False
        self.conn_FLAG = ["NO_MSG"]
    
    def recive_data(self) -> None:
        pass

    def send_data(self, data: str) -> None:
        pass
    
    