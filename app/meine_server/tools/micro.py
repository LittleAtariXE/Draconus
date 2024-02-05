import socket
import os

from random import randint



class MicroServer:
    def __init__(self, server_callback: object, file_len: int = 0, file_name: str = None, target_dir: str = None, work="download"):
        self.server = server_callback
        self.file_len = file_len
        self.file_name = file_name
        self.work = work
        self.ip = self.server.ip
        self.port = int(self.server.port) * 2 + randint(1, 700)
        self.noAttempts = 200
        self.outDir = os.path.join(self.server.config.get("OUTPUT_DIR"), self.server.name)
        self._is_working = False
        self.readyPort = None
        self.target_dir = target_dir
    
    def portAllocation(self) -> bool:
        att = 0
        while att < self.noAttempts:
            att += 1
            try:
                self.micro.bind((self.ip, self.port))
                return True
            except OSError:
                self.port += 3
        return False

    
    def buildServer(self) -> bool:
        self.micro = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.micro.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if not self.portAllocation():
            self.server.Msg("[!!] ERROR: Cant make micro server. [!!]", noI=True)
            return False
        else:
            try:
                self.micro.listen(1)
                self.micro.settimeout(5)
            except:
                self.server.Msg("[!!] ERROR: Cant make micro server. [!!]", noI=True)
                return False
            self.server.Msg(f"Micro Server create succcessfull: {self.ip}:{self.port}", dev=True)
            self.readyPort = self.port
            return True
    
    def saveFile(self, data: bytes) -> None:
        if not self.target_dir:
            name = os.path.join(self.outDir, self.file_name)
        else:
            name = os.path.join(self.target_dir, self.file_name)
        try:
            with open(name, "wb") as f:
                f.write(data)
            self.server.Msg(f"File: {self.file_name} save successfull", noI=True)
        except Exception as e:
            self.server.Msg(f"[!!] ERROR: Cant save file: {self.file_name}. {e} [!!]", noI=True)
    
    
    def downloadFile(self) -> None:
        try:
            self.conn, self.port = self.micro.accept()
        except TimeoutError:
            return None
        self.server.Msg(f"Start download file: {self.file_name}. Length: {self.file_len}", noI=True)
        data = b""
        try:
            while len(data) < self.file_len:
                recv = self.conn.recv(self.file_len - len(data))
                if not recv:
                    return None
                else:
                    data += recv
        except TimeoutError:
            self.server.Msg("[!!] Microserver socket timeout [!!]", dev=True)
        self.saveFile(data)
        self.conn.close()
    
    def uploadFile(self, fname: str) -> None:
        fpath = os.path.join(self.server.config["PAYLOAD_DIR"], fname)
        if not os.path.exists(fpath):
            self.server.Msg(f"[!!] ERROR: File name: {fname} does not exist in PAYLOAD dir [!!]")
            return
        try:
            self.conn, self.port = self.micro.accept()
        except TimeoutError:
            self.server.Msg("[!!] Microserver Timeout Error [!!]")
            return
        self.server.Msg(f"Start upload file: {fname}")
        try:
            with open(fpath, "rb") as f:
                self.conn.sendfile(f, 0)
        except Exception as e:
            self.server.Msg(f"[!!] ERROR: upload file: {fname} . Error: {e} [!!]")
            return
    

    
    


    
    def working(self) -> None:
        match self.work:
            case "download":
                self.downloadFile()
            case "upload":
                self.uploadFile(self.file_name)
    
    def START(self) -> None:
        self._is_working = True
        if self.buildServer():
            self.working()
        self._is_working = False
        try:
            self.micro.close()
        except:
            pass
        

        
        