import os

from pathlib import Path
from configparser import ConfigParser, ExtendedInterpolation
from typing import Union

class Configurator:
    def __init__(self):
        self.config = ConfigParser(interpolation=ExtendedInterpolation())
        self.pwd = os.path.dirname(__file__)
        self.cPath = os.path.join(Path(self.pwd).parent.parent, "CONFIG.ini")
        self.CONF = {}
        self.work()
    
    def ipAddrValidate(self, conf_ip: Union[int, str]) -> str:
        conf_ip = str(conf_ip)
        if conf_ip == '""':
            conf_ip = "127.0.0.1"
        elif conf_ip == "vps" or conf_ip == "VPS":
            conf_ip = ""
        return conf_ip
    
    def msgHeadValidate(self, sys_msg: str) -> str:
        if sys_msg == "gen" or sys_msg == "GEN" or sys_msg == '""':
            sys_msg = "generate"
        else:
            sys_msg = sys_msg.strip("'").strip('"')
        return sys_msg

    def readConf(self) -> None:
        self.config.read(self.cPath)
        _ip = self.config.get("BASIC", "IP")
        self.CONF["IP"] = self.ipAddrValidate(_ip)
        self.CONF["FORMAT_CODE"] = self.config.get("BASIC", "FORMAT_CODE")
        self.CONF["MSG_NO_IMPORTANT"] = self.config.getboolean("BASIC", "MSG_NO_IMPORTANT")
        self.CONF["MSG_VANILA_PRINT"] = self.config.getboolean("BASIC", "MSG_VANILA_PRINT")
        self.CONF["MSG_JSON"] = self.config.getboolean("BASIC", "MSG_JSON")
        self.CONF["RAW_LEN"] = int(self.config.get("ADVANCED", "RAW_LEN"))
        self.CONF["UNIX_RAW_LEN"] = int(self.config.get("ADVANCED", "UNIX_RAW_LEN"))
        self.CONF["ACCEPT_CONN_TIMEOUT"] = int(self.config.get("ADVANCED", "ACCEPT_CONN_TIMEOUT"))
        self.CONF["PROC_CYCLE_PAUSE"] = int(self.config.get("ADVANCED", "PROC_CYCLE_PAUSE"))
        self.CONF["UNIX_SOCKET_FORMAT"] = self.config.get("ADVANCED", "UNIX_SOCKET_FORMAT")
        self.CONF["MAIN_DIR"] = self.config.get("BASIC", "MAIN_DIR")
        self.CONF["HTTP_ENABLE"] = self.config.getboolean("BASIC", "HTTP_ENABLE")
        self.CONF["HTTP_ADMIN_ENABLE"] = self.config.getboolean("ADVANCED", "HTTP_ADMIN_ENABLE")
        self.CONF["PAUSE_OVERFLOW"] = self.config.get("ADVANCED", "PAUSE_OVERFLOW")
        self.CONF["AUTO_SAVE_SERVER"] = self.config.getboolean("BASIC", "AUTO_SAVE_SERVER")
        self.CONF["MSG_DEV"] = self.config.getboolean("DEV", "MSG_DEV")
        self.CONF["LOAD_ALL_SERVERS"] = self.config.getboolean("DEV", "LOAD_ALL_SERVERS")
        _head = self.config.get("HEADERS", "MSG_SYS_HEADERS")
        self.CONF["MSG_SYS_HEADERS"] = self.msgHeadValidate(_head)
        self.CONF["WORM_PAUSE_CONN"] = self.config.get("BASIC", "WORM_PAUSE_CONN")
        self.linkingDirs() 

    def linkingDirs(self) -> None:
        if self.CONF["MAIN_DIR"] == "main":
            self.CONF["MAIN_DIR"] = os.path.join(Path(self.pwd).parent.parent, "DRACO_FILES")
        self.CONF["APP_DIR"] = str(Path(self.pwd).parent)
        self.CONF["OUTPUT_DIR"] = os.path.join(self.CONF["MAIN_DIR"], self.config.get("DIRS", "OUTPUT_DIR"))
        self.CONF["UNIX_SOCKETS_DIR"] = os.path.join(self.CONF["MAIN_DIR"], self.config.get("DIRS", "SOCKET_DIR"))
        self.CONF["EXTRAS_DIR"] = os.path.join(self.CONF["MAIN_DIR"], self.config.get("DIRS", "EXTRAS_DIR"))
        self.CONF["PAYLOAD_DIR"] = os.path.join(self.CONF["MAIN_DIR"], "PAYLOAD")

    def work(self) -> None:
        self.readConf()


