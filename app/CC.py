import socket
import json
import os
import sys

from threading import Thread
from time import sleep
from typing import Union

from .draco_tools import Configurator
from .cc_tools import SocketHandler, ApiHandler


class CommandCenter:
    def __init__(self):
        self.conf = Configurator()
        self.conf = self.conf.CONF
        self.socksDir = self.conf.get("UNIX_SOCKETS_DIR", None)
        if not self.socksDir:
            print("[!!] ERROR: Missing config 'UNIX_SOCKETS_DIR' ... exit program [!!]")
            sys.exit()
        self.dracoSockFile = os.path.join(self.socksDir, "_draco_sock")
        self.dracoMsgFile = os.path.join(self.socksDir, "DRACONUS_msg")
        self.raw_len = self.conf.get("UNIX_RAW_LEN", 2048)
        self.format = self.conf.get("UNIX_SOCKET_FORMAT", "utf-8")
        self.SOCKETS = {}
        self.API = {}
    
    def findDraco(self) -> Union[object, bool]:
        if not os.path.exists(self.dracoSockFile):
            print("[SYSTEM] [!!] ERROR: Can not find Draconus [!!]")
            print("[SYSTEM] Propapbly Draconus was not started")
            return None
        ds = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            ds.connect(self.dracoSockFile)
            print("[SYSTEM] Find Draconus !!!")
            return ds
        except:
            print("[SYSTEM] [!!] ERROR: Can not connect to Draconus [!!]")
            print("[SYSTEM] Propapbly Draconus was not started")
            return None
    
    def connSocket(self, name: str):
        spath = os.path.join(self.socksDir, name)
        lsock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            lsock.connect(spath)
            self.SOCKETS[name[:-4]] = SocketHandler(name, lsock, self)
            self.SOCKETS[name[:-4]].start()
            return True
        except:
            return None
    
    def connApi(self, name: str):
        spath = os.path.join(self.socksDir, name)
        lsock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            lsock.connect(spath)
            self.API[name[:-4]] = ApiHandler(name, lsock, self)
            return True
        except:
            return None
    
    def findSockets(self, first_time=False):
        print("\n[SYSTEM] Finding servers ....")
        count = 0
        for fs in os.listdir(self.socksDir):
            if fs[-4:] == "_msg":
                if self.connSocket(fs):
                    count += 1
                sleep(0.2)
            if fs[-4:] == "_API":
                self.connApi(fs)
        if first_time:
            print(f"[SYSTEM] Finding {count -1} Servers")
    
    def sendCMD(self, *cmd : any) -> None:
        command = []
        for c in cmd:
            command.append(c)
        command = json.dumps(command)
        self.dracoSocket.sendall(command.encode(self.format))
    
    def reciveResponse(self) -> json:
        resp = b""
        while True:
            recv = self.dracoSocket.recv(self.raw_len)
            if recv:
                if len(recv) < self.raw_len:
                    resp += recv
                    break
                else:
                    resp += recv
            else:
                return None
        try:
            resp = json.loads(resp.decode(self.format))
            return resp
        except json.JSONDecodeError as e:
            print(f"[CC] [!!] ERROR: Json decode response [!!] : {e}")
            return None
    
    def sendApi(self, server_name: str, *cmd: any, response: bool = False) -> Union[bool, dict]:
        api = self.API.get(server_name)
        if not api:
            print("[CC] [!!] ERROR: API does not exist [!!]")
            return
        api.sendCMD(*cmd)
        if response:
            sleep(0.1)
            resp = api.reciveData()
            if not resp:
                print("[CC] [!!] ERROR: No Data recive")
                return None
            else:
                return resp




        
        
    def START(self) -> None:
        print("Command Center Start")
        print("Finding Draconus......")
        sleep(1)
        self.dracoSocket = self.findDraco()
        sleep(1)
        if not self.dracoSocket:
            print("EXIT PROGRAM")
            sys.exit()
        self.findSockets(True)       
        # sleep(2)
        # test = {"NAME" : "iza", "SERV_TYPE" : "Basic"}
        # self.sendCMD("make", test)
        # sleep(1)
        # self.findSockets()

        # print(self.API)
        # print(self.SOCKETS)

        # sleep(2)
        # self.API["iza"].sendCMD("conf")
        # sleep(0.2)
        # print(self.API["iza"].reciveData())

        # test = {"NAME" : "ania", "SERV_TYPE" : "Basic"}
        # self.sendCMD("make", test)
        # sleep(3)
        # self.findSockets()
        # input()




