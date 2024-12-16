
from typing import Union
from app.hive.Lib.tools.worm_var import WormVar



class ScriptItem:
    def __init__(self, fpath: str):
        self.fpath = fpath
        self.name = None
        self.types = None
        self.info = None

        # Compiler name
        self.compiler = None

        # required variables
        # SHEME: name##info##types##option1:value##option2:value2
        self.reqVar = {}

        # set variables
        # SHEME: name##value##types##option1:value##option2:value2
        self.setVar = {}

        # global variable. Use for compilation etc.
        # SHEME: var_name##value##[optional]info
        self.globalVar = {}

        

        self.make()
        
        
    @property
    def raw_code(self) -> str:
        return self.load_code()

    def load_item_data(self) -> list:
        data = []
        try:
            with open(self.fpath, "r") as file:
                raw = file.read()
        except:
            return []
        for line in raw.splitlines():
            if line == "#!CODE":
                break
            if line.startswith("#!"):
                data.append(line.lstrip("#!").rstrip("\n"))
        return data
    
    def load_code(self) -> str:
        code = ""
        try:
            with open(self.fpath, "r") as file:
                raw = file.read()
        except:
            return ""

        code_flag = False
        for line in raw.splitlines():
            if line == "" or line == "\n":
                continue
            if not code_flag:
                if line == "#!CODE":
                    code_flag = True
                    continue
                if line.startswith("#!"):
                    continue
            code += line + "\n"
        return code

    def extract_opt(self, headers: Union[list, None]) -> dict:
        if not headers:
            return {}
        opt = {}
        for h in headers:
            h = h.split(":")
            opt[h[0]] = h[1]
        return opt
    
    def add_reqVar(self, headers: list) -> None:
        if len(headers) > 3:
            opt = self.extract_opt(headers[3:])
        else:
            opt = {}
        if len(headers) < 3:
            types = "str"
        else:
            types = headers[2]
        req = WormVar(headers[0], info=headers[1], types=types, options=opt, owner_module=self.name)
        self.reqVar[req.name] = req
    
    def set_variable(self, headers: list) -> None:
        if len(headers) > 3:
            opt = self.extract_opt(headers[3:])
        else:
            opt = {}
        var = self.reqVar.get(headers[0])
        if not var:
            self.setVar[headers[0]] = WormVar(headers[0], headers[1], types=headers[2], options=opt, info="Variable automatically set")
            return
        var.options.update(opt)
        var.set_value(headers[1])
    

    
    def make(self) -> None:
        fdata = self.load_item_data()
        for d in fdata:
            d = d.split("##")
            match d[0]:
                case "name":
                    self.name = d[1]
                case "info":
                    self.info = d[1]
                case "types":
                    self.types = d[1]
                case "reqVar":
                    self.add_reqVar(d[1:])
                case "setVar":
                    self.set_variable(d[1:])
                case "Compiler":
                    self.compiler = d[1]
                