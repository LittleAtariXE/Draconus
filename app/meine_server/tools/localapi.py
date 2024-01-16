import os
import socket
import json

from typing import Dict, Any

class LocalAPI:
    def __init__(self, server_callback: object):
        self.server = server_callback
        self.sockets_dir = self.server.sockets_dir
        self.format = self.server.config.get("UNIX_SOCKET_FORMAT", "utf-8")
        self.raw_len = self.server.config.get("UNIX_RAW_LEN", 2048)
        self.sockFile = os.path.join(self.sockets_dir, f"{self.server.name}_API")
    
    def build(self) -> bool:
        if os.path.exists(self.sockFile):
            try:
                os.unlink(self.sockFile)
            except OSError as e:
                self.server.Msg(f"[!!] ERROR: Local API unlink socket file: {e} [!!]")
                return False
        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            self.socket.bind(self.sockFile)
            self.socket.listen()
            return True
        except OSError as e:
            self.server.Msg(f"[!!] ERROR: Bind Local API socket: {e} [!!]")
            return False
        
    def acceptConn(self) -> None:
        self.conn, self.addr = self.socket.accept()
    
    def recvMsg(self) -> Dict:
        msg = b""
        while True:
            recv = self.conn.recv(self.raw_len)
            if not recv:
                return None
            else:
                if len(recv) < self.raw_len:
                    msg += recv
                    break
                else:
                    msg += recv
        return msg.decode(self.format)
    
    def recvJson(self) -> None:
        try:
            data = self.recvMsg()
        except:
            return None
        if not data:
            return None
        else:
            data = json.loads(data)
            return data
    
    def sendJson(self, data:dict[any]) -> None:
        try:
            data = json.dumps(data)
        except json.JSONDecodeError as e:
            self.server.Msg(f"[!!] ERROR: Local API: Json encode error: {e} [!!]")
            return
        try:
            self.conn.sendall(data.encode(self.format))
        except OSError as e:
            self.server.Msg(f"[!!] ERROR: Local API: Json send data error: {e} [!!]")

    
    def _execCMD(self, data: list) -> None:
        self.server.Msg(f"Local API Command: {data}", dev=True)
        if not isinstance(data, list):
            self.server.Msg("[!!] ERROR: Wrong Local API command syntax. Must be a list [!!]")
            return
        match data[0]:
            case "cmd":
                self.server.Ctrl._execCMD(data[1:])
            case "conf":
                self.sendJson(self.server.config)
            case _:
                self.execCMD(data)
    
    def execCMD(self, data: list) -> None:
        self.server.Msg("[!!] Unknown LocalAPI Command [!!]")

    def START(self) -> None:
        if self.build():
            self.server.Msg("Local API build successfull", dev=True)
            while True:
                self.acceptConn()
                self.server.Msg("Connected to local API", dev=True)
                while True:
                    recv = self.recvJson()
                    if not recv:
                        break
                    else:
                        self.server.Msg(f"LocalAPI recive JSON: {recv}", dev=True)
                        self._execCMD(recv)

