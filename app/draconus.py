import os
import socket
import sys
import json

from multiprocessing import Pipe
from threading import Thread
from typing import Union
from time import sleep

from .meine_server import Basic, Echo
from .meine_server import Messenger
from .draco_tools import Configurator, ServerHandler
from .hive import Queen


class Draconus:
    def __init__(self):
        self.config = Configurator()
        self.socketsDir = self.config.CONF["UNIX_SOCKETS_DIR"]
        self._socketFile = os.path.join(self.socketsDir, "_draco_sock")
        self.SERVERS = {}
        self._pauseClean = False
        self.baseServers = {
            Basic.SERV_TYPE : Basic,
            Echo.SERV_TYPE : Echo}


    
    @property
    def conf(self) -> dict:
        return self.config.CONF
    
    def makeFile(self) -> None:
        if not os.path.exists(self.conf["MAIN_DIR"]):
            os.mkdir(self.conf["MAIN_DIR"])
        if not os.path.exists(self.conf["OUTPUT_DIR"]):
            os.mkdir(self.conf["OUTPUT_DIR"])
        if not os.path.exists(self.conf["UNIX_SOCKETS_DIR"]):
            os.mkdir(self.conf["UNIX_SOCKETS_DIR"])
    
    def cleaner(self) -> None:
        for fs in os.listdir(self.socketsDir):
            try:
                os.unlink(os.path.join(self.socketsDir, fs))
            except:
                pass
    
    def buildServer(self) -> bool:
        try:
            self.server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.server.bind(self._socketFile)
            self.server.listen(1)
            self.raw_len = self.conf.get("UNIX_RAW_LEN", 2048)
            self.format = self.conf.get("UNIX_SOCKET_FORMAT", "utf-8")
            self.Msg("Socket Server build successfull")
            return True
        except Exception as e:
            self.Msg(f"[!!] ERROR: Cant build socket server: {e}")
            return False
        
    def build(self) -> None:
        self.makeFile()
        config = self.conf.copy()
        config.update({"NAME" : "DRACONUS"})
        self.cleaner()
        self.Msg = Messenger(config)
        self.Msg.START()      
        if not self.buildServer():
            self.Msg("[!!] DRACONUS EXIT [!!]")
            sys.exit()
    
    def acceptConn(self) -> None:
        self.conn, self.addr = self.server.accept()
        self.Msg("Connected to Draconus")
    

    def recvJson(self) -> Union[list, bool]:
        data = b""
        while True:
            recv = self.conn.recv(self.raw_len)
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
        except json.JSONDecodeError as e:
            self.Msg(f"[!!] ERROR: decode JSON command [!!] : {e}")
            self.Msg(f"Recived data: {data}", dev=True)
        return data
    
    def sendJson(self, data) -> None:
        try:
            data = json.dumps(data)
        except json.JSONDecodeError as e:
            self.Msg(f"[!!] ERROR: {e}")
            return
        try:
            self.conn.sendall(data.encode(self.format))
        except Exception as e:
            self.Msg(f"[!!] ERROR: sending data from Draconus to Command Center [!!] : {e}")



####################################################################  
 
    def checkPortAva(self, port: str) -> bool:
        for ser in self.SERVERS.values():
            if port == str(ser.server.port):
                return False
        return True

    def makeNewServer(self, config) -> None:
        self._pauseClean = True
        conf = self.conf.copy()
        conf.update(config)
        if conf["NAME"] in self.SERVERS.keys():
            self.Msg("[!!] ERROR: A server with this name already exist [!!]")
            return False
        if not conf.get("PORT"):
            self.Msg("[!!] WARNING: No port number specified. Allocation attempt to a random number. [!!]")
        else:
            if not self.checkPortAva(conf["PORT"]):
                self.Msg("[!!] ERROR: This port number is already use [!!]")
                return False
        new = self.baseServers.get(conf["SERV_TYPE"])
        if not new:
            self.Msg(f"[!!] ERROR: this server types: {conf['SERV_TYPE']} does not exist [!!]")
            return False
        tD, tS = Pipe()
        server = new(tS, conf)
        self.SERVERS[conf["NAME"]] = ServerHandler(conf["NAME"], tD, server, self)
        self.SERVERS[conf["NAME"]].begin()
        sleep(1)
        self._pauseClean = False

    def killServer(self, name: str) -> None:
        sname = self.SERVERS.get(name)
        if not sname:
            self.Msg(f"[!!] ERROR: Server with name: {name} does not exist [!!]")
            return
        self.Msg(f"Preapre to stopping server <{name}>")
        sname.sendCmd(["serv", "end"])
        sleep(1)
        del self.SERVERS[name]
    
    def showServerTypes(self) -> None:
        info = {}
        for st in self.baseServers.keys():
            info[st] = self.baseServers[st].SERV_INFO
        self.Msg(info, dictFormat=True, dictName="Avaible Server Types")
    
    def showServers(self) -> None:
        if len(self.SERVERS) < 1:
            self.Msg("No Servers Created !")
            return
        for serv in self.SERVERS.values():
            serv.sendCmd(["serv", "conf"])
            sleep(0.1)
    
    def showServerList(self) -> None:
        if len(self.SERVERS) < 1:
            self.Msg("No Servers Created !")
            return
        buff = ""
        for serv in self.SERVERS.values():
            buff += f"\n** {serv.server.name} -- {serv.server.SERV_TYPE}"
        self.Msg(f"\n ***** Created server list ********{buff}")


    
    def forwardMsg(self, cmd) -> None:
        serv = self.SERVERS.get(cmd[1])
        if not serv:
            self.Msg("[!!] Error: Server with this name does not exist [!!]")
            return
        serv.sendCmd(cmd[2:])

    def checkServer(self, serv_name : str) -> None:
        if serv_name in self.SERVERS.keys():
            self.sendJson(["OK"])
        else:
            self.Msg("[!!] ERROR: Server with this name does not exists [!!]")
            self.sendJson(["NOT"])
    
    def startServer(self) -> None:
        for serv in self.SERVERS.values():
            serv.sendCmd(["serv", "start"])
    
    def stopServer(self) -> None:
        for serv in self.SERVERS.values():
            serv.sendCmd(["serv", "stop"])
        


    
    def exitDraco(self) -> None:
        self.Msg("Prepare to stopping servers")
        for serv in self.SERVERS.values():
            serv.sendCmd(["serv", "end"])
        sleep(2)
        self.Msg("[SYSTEM] DRACONUS STOPPED")
        self.cleaner()
        sys.exit()
#################################################################    
    def serverCleaner(self) -> None:
        tooDel = []
        for serv_name, serv_hand in self.SERVERS.items():
            if not serv_hand.working:
                tooDel.append(serv_name)
                self.Msg(f"Clear stopped/broken server: {serv_hand.name}", dev=True)
        for td in tooDel:
            del self.SERVERS[td]
    
    def _cycleCleaner(self) -> None:
        while True:
            if not self._pauseClean:
                self.serverCleaner()
            sleep(3)
    
    def cycleCleaner(self) -> None:
        self.Cleaner = Thread(target=self._cycleCleaner, daemon=True)
        self.Cleaner.start()
#######################################################################

    def hive(self, conf: dict) -> None:
        self.Queen.hatchering(conf)

#######################################################################
    
    def execCmd(self, cmd) -> None:
        match cmd[0]:
            case "make":
                self.makeNewServer(cmd[1])
            case "end":
                self.exitDraco()
            case "kill":
                self.killServer(cmd[1])
            case "showT":
                self.showServerTypes()
            case "showS":
                self.showServers()
            case "showL":
                self.showServerList()
            case "startS":
                self.startServer()
            case "stopS":
                self.stopServer()
            case "next":
                self.forwardMsg(cmd)
            case "check":
                self.checkServer(cmd[1])
            case "hive":
                self.hive(cmd[1])

            case _:
                self.Msg("[!!] Unknown Command [!!]")

    
    def START(self) -> None:    
        self.build()
        self.Msg("[!!] DRACONUS START ... waiting for commands [!!]")
        self.Queen = Queen(self)
        self.cycleCleaner()
        while True:
            self.acceptConn()
            while True:
                cmd = self.recvJson()
                if not cmd:
                    break
                # self.Msg(f"CMD: {cmd}")
                self.execCmd(cmd)
        








