import socket
import os

from threading import Thread, Event
from time import sleep



class Server(Thread):
    def __init__(self, draco_callback: object, name: str, port: int, options: dict = {}):
        super().__init__()
        self._options = options
        self.draco = draco_callback
        self.Central = self.draco.Central
        self.msg = self.draco.msg
        self.name = name
        self.port = int(port)
        self.ip = self.draco.config.ip
        self.working_FLAG = Event()
        self.working_FLAG.clear()
        self.to_listening = self.draco.config.tcp_sock_to_listening
        self.build_FLAG = None
        self._protocol_type = {
            "default" : "TcpHandler",
            "raw" : "TcpRawHandler",
            "down" : "TcpRawDownloader",
            "send" : "TcpRawSend"
        }
        self.protocol_type = self._protocol_type[options.get("PROTOCOL_TYPE", "default")]
        if options.get("PROTOCOL_TYPE") == "send":
            dir_in = self.draco.config.dir_in
            if not os.path.exists(os.path.join(dir_in, self.name)):
                os.mkdir(os.path.join(dir_in, name))
                
    

    def build_server(self) -> bool:
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server.bind((self.ip, self.port))
        except OSError as e:
            self.msg("error", f"[!!] ERROR Build Server: {e} [!!]")
            return False
        self.msg("msg", f"Server: <{self.name}> on port {self.port} build successfull")
        return True
    
    def listening(self) -> None:
        if not self.working_FLAG.is_set():
            self.msg("error", "[!!] Server can not listening [!!]", sender=self.name)
            return
        self.server.settimeout(self.to_listening)
        self.server.listen()
        self.msg("msg", f"Server Start Listening .... waiting for connections ...", sender=self.name)
        self.build_FLAG = True
        while self.working_FLAG.is_set():
            try:
                conn, addr = self.server.accept()
                self.Central.add_connection(conn, addr, self.name, self.protocol_type)
            except TimeoutError:
                continue
            except OSError as e:
                self.msg("error", f"[!!] ERROR: accepting connections: {e} [!!]", sender=self.name)
                return
        self.msg("msg", "Server Stop Listening .... close connection ... ", sender=self.name)
        self.close()
    
    def close(self) -> None:
        self.working_FLAG.clear()
        sleep(self.to_listening)
        for cli in self.Central.clients.values():
            if cli.server_name == self.name:
                cli.close()
        try:
            self.server.close()
        except:
            pass
        self.msg("msg", "Server Closed", sender=self.name)


    def run(self) -> None:
        self.working_FLAG.set()
        if self.build_server():
            self.listening()