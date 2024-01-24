import os
import socket
import string
import threading
import sys

from multiprocessing import Process, Pipe
from threading import Thread
from time import sleep
from random import randint

from .tools.messenger import Messenger
from .tools.tasker import Tasker
from .tools.controlers import BasicControler
from .tools.chameleon import Chameleon
from .tools.handlers import ConnCentral
from .tools.headers import MrHeader
from .tools.httpapi import HttpAPI
from .tools.localapi import LocalAPI
from .tools.micro import MicroServer



class BasicTemplate(Process):
    SERV_TYPE = None
    SERV_INFO = None
    WORM_INFO = None
    def __init__(self, ctrl_pipe: Pipe, conf: dict = {}, messenger: object = Messenger, controlers: object = BasicControler, localApi=LocalAPI):
        super().__init__(daemon=True)
        self._oldConf = conf
        self.name = conf.get("NAME", self.generateName())
        self.ip = conf.get("IP", "127.0.0.1")
        self.port = conf.get("PORT", None)
        self._portAttempt = 100
        self.format = conf.get("FORMAT_CODE", "utf-8")
        self.raw_len = conf.get("RAW_LEN", 2048)
        self.sockets_dir = conf.get("UNIX_SOCKETS_DIR", os.path.join(os.path.dirname(__file__), "_sockets"))
        self._accConnTO = conf.get("ACCEPT_CONN_TIMEOUT", 3)
        self._pauseWork = conf.get("PROC_CYCLE_PAUSE", 2)
        self.sysHeadears = conf.get("MSG_SYS_HEADERS", MrHeader().generate_name())
        self._http_enable = conf.get("HTTP_ENABLE", False)
        self._pauseOverflow = float(conf.get("PAUSE_OVERFLOW", 0.2))
        self.ctrl_pipe = ctrl_pipe
        self.__CHAM = Chameleon
        self.Cham = None
        self.__MSG = messenger
        self.Msg = None
        self.__CENTRAL = ConnCentral
        self.Central = None
        self.is_listening = False
        self.working = False
        self.__TASKER = Tasker
        self.__CTRL = controlers
        self.__HTTP = HttpAPI
        self.__LOCAPI = localApi
        self.LocApi = None
        self.Http = None
        self.httpAddr = None
        self.Ctrl = None
        self.Tasker = None
        self.ready2rebuild = False
        self._killMe = False
    
    @property
    def config(self) -> dict :
        conf = {
            "NAME" : self.name,
            "IP" : self.ip,
            "PORT" : self.port,
            "FORMAT_CODE" : self.format,
            "RAW_LEN" : self.raw_len,
            "UNIX_SOCKETS_DIR" : self.sockets_dir,
            "ACCEPT_CONN_TIMEOUT" : self._accConnTO,
            "PROC_CYCLE_PAUSE" : self._pauseWork,
            "LISTENING" : self.is_listening,
            "SYS_MSG_HEADERS" : self.sysHeadears,
            "HTTP_ADDR" : str(self.httpAddr),
            "SERV_TYPE" : self.SERV_TYPE,
            "SERV_INFO" : self.SERV_INFO,
            "WORM_INFO" : self.WORM_INFO,
            "PAUSE_OVERFLOW" : self._pauseOverflow
        }
        tmp = self._oldConf.copy()
        tmp.update(conf)      
        return tmp

    def generateName(self, number: int = 4) -> str:
        temp = string.ascii_lowercase
        count = 0
        text = ""
        while count < number:
            char = randint(0, len(temp) -1)
            text += temp[char]
            count += 1
        return text
    
    def beforeStart(self) -> None:
        if not os.path.exists(self.sockets_dir):
            os.mkdir(self.sockets_dir)
        self.Tasker = self.__TASKER(self)
        self.Msg = self.__MSG(self.config, self.Tasker)
        self.Msg.START()
        self.Tasker._update()

    
    ################# Build and Listening ########################################
    def portAllocation(self) -> bool:
        count = 0
        while count < self._portAttempt:
            self.port = randint(1000, 9999)
            try:
                self.server.bind((self.ip, self.port))
                return True
            except OSError:
                count += 1
                continue
        return None

    def build(self, first_time : bool = True) -> bool:
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except OSError as error:
            self.Msg(f"[!!] ERROR: Socket created: {error} [!!]")
            return False

        if not self.port:
            if not self.portAllocation():
                self.Msg("[!!] ERROR: bind socket server. Cant port allocation [!!]")
                return False
        else:
            try:
                self.port = int(self.port)
                self.server.bind((self.ip, self.port))
            except (ValueError, TypeError):
                self.Msg(f"[!!] ERROR: Wrong port number: {self.port}")
                return False
            except OSError as e:
                self.Msg(f"[!!] ERROR bind socket !!! ... propably wrong IP address [!!] : {e}")
                return False
        if first_time:
            self.Ctrl = self.__CTRL(self.ctrl_pipe, self)
            self.Tasker.addTask(name=self.Ctrl.name, func_name=self.Ctrl.START, info="Server Command Controler")
            self.Cham = self.__CHAM(self.format)
            if self._http_enable:
                self.Http = self.__HTTP(self, admin_enable=self.config.get("HTTP_ADMIN_ENABLE"))
                self.Tasker.addTask(name="HTTP SERVER", func_name=self.Http.START, info="Http Server Thread")
                self.httpAddr = f"{self.ip}:{self.Http.port}"
            self.LocApi = self.__LOCAPI(self)
            self.Tasker.addTask(name="LocAPI", func_name=self.LocApi.START, info="Local API Thread")       
            sleep(0.5)
            self.Msg(f"Server created successfull. Address: {self.ip}:{self.port}")
            self.ctrl_pipe.send(["OK"])
        else:
            self.Msg("Socket rebuild successfull")
        
        self.working = True
        self.ready2rebuild = False
        return True
    
    def _listening(self) -> None:
        self.server.listen()
        self.is_listening = True
        self.server.settimeout(self._accConnTO)
        self.Central = self.__CENTRAL(self, self.Msg, self.Cham)
        self.Msg("Server start listening ... waiting for connection ....")
        while self.is_listening:
            try:
                conn, addr = self.server.accept()
                self._accept_conn(conn, addr)
            except socket.timeout:
                continue
        self.Msg("Server stop listening")
        self.server.close()
        if not self._killMe:
            self.ready2rebuild = True
        self.Central = None
        return
    
    def listening(self) -> None:
        if self.is_listening:
            self.Msg("Server already listening")
            return
        self.Tasker.addTask(name="Listening TH", func_name=self._listening, info="Accept Connection Threading", is_daemon=False)
    
    def stopListening(self) -> None:
        if not self.is_listening:
            self.Msg("Server not listening")
            return
        self.Msg("Preapre to disconnecting clients and stop listening .....")
        self.is_listening = False



    
    def _accept_conn(self, conn : object, addr: object):
        client = self.Central.addClient(conn, addr)
        self.acceptConn(client)
    
    def acceptConn(self, client: object) -> None:
        pass
    




    ################################ OTHERS ###########################################
    def workCycle(self) -> None:
        if self.ready2rebuild:
            self.build(False)
        if self.Central:
            self.Central.clear()
        self.Tasker.cleaner()

        
    def turnOFF(self) -> None:
        self.is_listening = False
        self._killMe = True
        self.Msg("Signal to stop")
        self.working = False
        sleep(self._accConnTO)
        self.Msg("[!!] Stoping Server [!!]")
        sleep(1)

    def run(self) -> None:
        self.beforeStart()
        if self.build():
            while self.working:
                self.workCycle()
                sleep(self._pauseWork)
        self.Msg("Server Closed")
        sys.exit()

        
        
            

        
class AdvTemplate(BasicTemplate):
    SERV_TYPE = None
    SERV_INFO = None
    WORM_INFO = None
    def __init__(self, ctrl_pipe: Pipe, conf: dict = {}, messenger: object = Messenger, controlers: object = BasicControler, localApi=LocalAPI):
        super().__init__(ctrl_pipe=ctrl_pipe, conf=conf, messenger=messenger, controlers=controlers, localApi=localApi)
        self.__xtraServ = MicroServer
        self.outDIR = os.path.join(self.config["OUTPUT_DIR"], self.name)
        if not os.path.exists(self.outDIR):
            os.mkdir(self.outDIR)

    
        