import socket
import os



class MicroServer:
    def __init__(self, server_callback: object, file_len: int = 0, file_name: str = None, work="download"):
        self.server = server_callback
        self.file_len = file_len
        self.file_name = file_name
        self.work = work
        self.ip = self.server.ip
        self.port = int(self.server.port) * 2
        self.noAttempts = 100
        self.outDir = os.path.join(self.server.config.get("OUTPUT_DIR"), self.server.name)
        self._is_working = False
        self.readyPort = None
    
    def portAllocation(self) -> bool:
        att = 0
        while att < self.noAttempts:
            att += 1
            try:
                self.micro.bind((self.ip, self.port))
                return True
            except OSError:
                self.port += 1
        return False

    
    def buildServer(self) -> bool:
        self.micro = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.micro.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if not self.portAllocation():
            self.server.Msg("[!!] ERROR: Cant make micro server. [!!]")
            return False
        else:
            try:
                self.micro.listen(1)
            except:
                self.server.Msg("[!!] ERROR: Cant make micro server. [!!]")
                return False
            self.server.Msg(f"Micro Server create succcessfull: {self.ip}:{self.port}", dev=True)
            self.readyPort = self.port
            return True
    
    def saveFile(self, data: bytes) -> None:
        name = os.path.join(self.outDir, self.file_name)
        try:
            with open(name, "wb") as f:
                f.write(data)
            self.server.Msg(f"Save file: {self.file_name} save successfull", noI=True)
        except Exception as e:
            self.server.Msg(f"[!!] ERROR: Cant save file: {self.file_name}. {e} [!!]", noI=True)
    
    
    def downloadFile(self) -> None:
        self.conn, self.port = self.micro.accept()
        self.server.Msg(f"Start download file: {self.file_name}. Length: {self.file_len}", noI=True)
        data = b""
        while len(data) < self.file_len:
            recv = self.conn.recv(self.file_len - len(data))
            if not recv:
                return None
            else:
                data += recv
        self.saveFile(data)
    
    def working(self) -> None:
        match self.work:
            case "download":
                self.downloadFile()

    
    def START(self) -> None:
        self._is_working = True
        if self.buildServer():
            self.working()
        self._is_working = False

        
        