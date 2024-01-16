import socket
import json


class ApiHandler:
    def __init__(self, name : str, api_socket : socket, cc_calback: object):
        self.name = name
        self.socket = api_socket
        self.CC = cc_calback
        self.raw_len = self.CC.raw_len
        self.format = self.CC.format
    
    def sendCMD(self, *cmd : any) -> None:
        command = []
        for c in cmd:
            command.append(c)
        try:
            command = json.dumps(command)
        except json.JSONDecodeError as e:
            print("[SYSTEM] [!!] ERROR: Send command to api server: ", e)
            return
        try:
            self.socket.sendall(command.encode(self.format))
        except (BrokenPipeError, ConnectionAbortedError) as e:
            print("[SYSTEM] ERROR: Send command to api server: ", e)
            return
    
    def reciveData(self) -> any:
        data = b""
        while True:
            recv = self.socket.recv(self.raw_len)
            if recv:
                if len(recv) < self.raw_len:
                    data += recv
                    break
                else:
                    data += recv
            else:
                return None
        data = data.decode(self.format)
        try:
            data = json.loads(data)
            return data
        except json.JSONDecodeError as e:
            print("[SYSTEM] ERROR: decode json data: ", e)
            return None