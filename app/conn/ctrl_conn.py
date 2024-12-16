import socket
import os

from app.conn.protocols.unix_handler import UnixHandler
from app.controlers.draco_control import DracoControler


class ControlConnector:
    def __init__(self, draco_callback: object):
        self.draco = draco_callback
        self.ctrl_path = self.draco.config.socket_draco_ctrl
        self.msg = self.draco.msg
        self.socket_to = self.draco.config.unix_sock_to_recive
        self.raw_len = self.draco.config.unix_socket_raw_len
        self.format = self.draco.config.unix_socket_format
        self.separator = self.draco.config.unix_socket_separator
        self.Ctrl = DracoControler(self.draco)
    
    
    def build(self) -> bool:
        if os.path.exists(self.ctrl_path):
            try:
                os.unlink(self.ctrl_path)
            except:
                pass
        try:
            self.server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.server.bind(self.ctrl_path)
            self.server.listen(1)
            self.msg("msg", "Control Socket Build Successfull")
            return True
        except Exception as e:
            self.msg("error", f"[!!] ERROR Build Control Socket: {e} [!!]")
            return False
    

    def accept_conn(self) -> None:
        self.server.settimeout(self.socket_to)
        while self.draco.working_FLAG.is_set():
            try:
                self.conn, self.addr = self.server.accept()
            except TimeoutError:
                continue
            self.msg("msg", "Connected to Draconus")
            self.ctrl = UnixHandler(self.draco.working_FLAG, self.conn, self.raw_len, self.format, self.separator, self.socket_to)
            self.recive_CMD()
    
    def _recive_CMD(self) -> None:
        while self.draco.working_FLAG.is_set():
            try:
                recv = self.ctrl.recive_data()
            except TimeoutError:
                continue
            if not recv:
                break
            self.Ctrl.check_command(recv)
    
    def recive_CMD(self) -> None:
        cmd = self.draco.Task.add_task("Commander", self._recive_CMD, info="Recive commands from Commander", is_daemon=False)

    def send_data(self, data: dict) -> None:
        self.ctrl.send_data(data)
        

    
    def Start(self) -> bool:
        if not self.build():
            return False
        self.draco.Task.add_task("Draco_controler", self.accept_conn, info="Connection beetwen Draconus and CC")
        return True
