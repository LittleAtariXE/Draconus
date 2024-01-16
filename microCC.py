import socket
import json
import os

from time import sleep

from app.draco_tools import Configurator

class MicroCC:
    def __init__(self):
        self.config = Configurator()
        self.sockDIR = self.config.CONF["UNIX_SOCKETS_DIR"]
        self.format = self.config.CONF["UNIX_SOCKET_FORMAT"]
        self.dracoSock = os.path.join(self.sockDIR, "_draco_sock")

        self.defConf = {"NAME" : "ala", "SERV_TYPE" : "Basic"}
    
    def conn2draco(self):
        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            self.socket.connect(self.dracoSock)
            print("CONNECTED")
        except Exception as e:
            print("ERROR: ", e)
    
    def sendCMD(self, *cmd):
        data = []
        for c in cmd:
            data.append(c)
        data = json.dumps(data)
        try:
            self.socket.sendall(data.encode(self.format))
        except Exception as e:
            print("ERRPR: ",e)
    

if __name__ == "__main__":
    CC = MicroCC()
    CC.conn2draco()
    CC.sendCMD("make", CC.defConf)
    sleep(2)
    CC.sendCMD("showT")
    # CC.sendCMD("kill", "ala")
    # sleep(3)
    # CC.sendCMD("make", CC.defConf)
