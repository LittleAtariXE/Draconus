import os
from typing import Union
from .worm_var import WormVar
from .garbage_var import GarbageVar

LIBRARY_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LIBRARY_DIR_BINARY = os.path.join(LIBRARY_DIR, "items", "binary")


class LibItem:
    def __init__(self, fpath: str):
        self.fpath = fpath
        self._headers = None
        self._separator = "##"

        # module name
        self.name = None
        # module types
        self.types = None
        # module subtypes
        # loader - Places code first for execution.
        self.subTypes = None
        # module info
        self.info = None
        # source code from external file
        self.source = None
        
        # Special 'tag' for marking modules
        # 'loader' - 
        # 'dll' - DLL code is not included with the main code.
        self.subTypes = None

        # Accepted modules. Subtype of modules that can be added.
        # 'dll' - only dll is accepted
        self.acceptMods = []

        ########### required variables ##########
        # SHEME: name##info##types##option1:value##option2:value2
        # Variables starting with “_COMP_” are passed to compiler variables.
        # Variables starting with "_" are passed to payload 'IN' options. Ex: _encode_b64_opt_exe##True
        # Variables starting with "__" are passed to payload 'OUT' options. Ex: __encode_b64_opt_exe##True
        # Variables starting with "DLL_" are passed to DLL Struct
        # Variables starting with "GLOBAL_" are passed to globalVar
        self.reqVar = {}
        # Food represent special variables from library
        # SHEME: code_name_var##library_var_name##info##option1:value1##option2:value2
        self.reqFood = {}

        # set variables
        # SHEME: name##value##types##option1:value##option2:value2
        # Variables starting with “_COMP_” are passed to compiler variables.
        self.setVar = {}

        # Required modules
        self.reqMod = []
        # Required support modules
        self.reqSMod = []
        # Required payloads
        # SHEME: name##info##option1:value1##option2:value2
        self.reqPayload = {}
        # Payload option
        # SHEME: payloadOpt##name##option##value

        # Second Payload option. Used inside 'payload' code.
        # SHEME: payOpt##name##value
        self.payOpt = {}

        # New function 'Payload Step Pipeline'
        # SHEME: payStep##PAYLOAD_STEP
        # SHEME: payStep##PAYLOAD_STEP$TARGET_PAYLOAD
        self.payStep = []


        # global variable. Use for compilation etc.
        # SHEME: var_name##value##[optional]info
        self.globalVar = {}

        #Special variables called 'junk' that make code difficult to read.
        #SHEME: var_name##default_value##types_convert##[optional]info
        self.garbageVar = {}

        # Coder options used when creating code.
        # SHEME: option##value
        # FORMAT##PS_SCRIPT     - Format code to PS script
        self.coderOpt = {}
        
        # binary - name of binary file
        self.binary = None

        #Worm elements that cannot be added
        ## SHEME EX: module##shadow
        self.banned = []

        # name of code language
        self.lang = None
        # flag for single template rendering
        self.render_FLAG = None
        # flag for including imports in code
        self.import_FLAG = False
        # flag for Without extracting 'imports' outside the code
        self.no_extract_FLAG = False

        # On what system will the module be able to run
        # [LW] = Linux and Windows
        # [W] = only Windows
        # [L] = only Linux
        self.system_FLAG = "[LW]"

        # Object options. Additional options for the object.
        # Options startswith "DLL_" are passed to DLL Struct
        # Options startswith "WORM_" are passed to WormConstructor RawWorm object
        self.options = {}

        # special tag for payload
        self.owner = None

        # Set process worm code
        self.processWorm = None

        # Compiler compatibility (for CScript)
        self.compiler_compatibility = []

        # required Compiler Script
        # reqCS##<name>
        self.reqCS = None

        # SPECIAL TAGS:
        ### 
        self.tags = ""

        #A module marked as 'broken' will not be loaded.
        self.broken_FLAG = False

        ### MAKE
        self.make()

    @property
    def raw_code(self) -> str:
        return self.load_code()
    
    @property
    def bin_code(self) -> Union[None, bytes]:
        return self.load_bin()
    


    def load_item_data(self) -> list:
        data = []
        try:
            with open(self.fpath, "r") as file:
                raw = file.read()
        except:
            self.broken_FLAG = True
            return []
        for line in raw.splitlines():
            if line == "#!CODE":
                break
            if line.startswith("#!"):
                data.append(line.lstrip("#!").rstrip("\n"))
        return data
    
    def load_code(self) -> str:
        code = ""
        if self.source:
            fpath = self.source
        else:
            fpath = self.fpath
        try:
            with open(fpath, "r") as file:
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
    
    def load_bin(self) -> Union[None, bytes]:
        if not self.binary:
            return None
        try:
            with open(os.path.join(LIBRARY_DIR_BINARY, self.binary), "rb") as file:
                data = file.read()
            return data
        except:
            return None
    
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
            # self.msg("error", f"[!!] ERROR: Missing config in module template: '{self.name}' [!!]")
            return
        var.options.update(opt)
        var.set_value(headers[1])

    
    def add_reqFood(self, headers: list) -> None:
        if len(headers) > 3:
            opt = self.extract_opt(headers[3:])
        else:
            opt = {}
        food = WormVar(headers[1], info=headers[2], options=opt)
        self.reqFood[headers[0]] = food

    def add_reqPayload(self, headers: list) -> None:
        if len(headers) > 2:
            opt = self.extract_opt(headers[2:])
        else:
            opt = {}
        req = WormVar(headers[0], info=headers[1], options=opt, owner_module=self.name)
        self.reqPayload[headers[0]] = req
    
    def add_payload_options(self, headers: list) -> None:
        pay = self.reqPayload.get(headers[0])
        if not pay:
            return
        pay.options[headers[1]] = headers[2]
    
    def add_global_var(self, headers: list) -> None:
        info = headers[2] if len(headers) > 2 else ""
        gvar = WormVar(headers[0], headers[1], info=info)
        self.globalVar[gvar.name] = gvar
    
    def add_garbage_var(self, headers: list) -> None:
        name = headers[0]
        bytes_count = headers[1]
        sheme = headers[2]
        if len(headers) > 3:
            info = headers[3]
        else:
            info = ""
        self.garbageVar[name] = GarbageVar(name, bytes_count, sheme, info)
    
    def add_options(self, headers: list) -> None:
        self.options[headers[0]] = headers[1]


    def make(self) -> None:
        fdata = self.load_item_data()
        for d in fdata:
            d = d.split(self._separator)
            match d[0]:
                case "name":
                    self.name = d[1]
                case "info":
                    self.info = d[1]
                case "types":
                    self.types = d[1]
                case "subTypes":
                    self.subTypes = d[1]
                case "reqVar":
                    self.add_reqVar(d[1:])
                case "setVar":
                    self.set_variable(d[1:])
                case "reqMod":
                    self.reqMod.extend(d[1:])
                case "reqSMod":
                    self.reqSMod.extend(d[1:])
                case "reqFood":
                    self.add_reqFood(d[1:])
                case "reqPayload":
                    self.add_reqPayload(d[1:])
                case "payloadOpt":
                    self.add_payload_options(d[1:])
                case "binary":
                    self.binary = os.path.join(LIBRARY_DIR_BINARY, d[1])
                case "banned":
                    self.banned.extend(d[1:])
                case "lang":
                    self.lang = d[1]
                case "render_FLAG":
                    self.render_FLAG = d[1]
                case "system_FLAG":
                    self.system_FLAG = d[1]
                case "import_FLAG":
                    self.import_FLAG = d[1]
                case "globalVar":
                    self.add_global_var(d[1:])
                case "coderOpt":
                    self.coderOpt[d[1]] = d[2]
                case "processWorm":
                    self.processWorm = d[1]
                case "garbageVar":
                    self.add_garbage_var(d[1:])
                case "subTypes":
                    self.subTypes = d[1]
                case "options":
                    self.add_options(d[1:])
                case "no_extract_FLAG":
                    if d[1] == False or d[1] == "False":
                        self.no_extract_FLAG = False
                    else:
                        self.no_extract_FLAG = True
                case "payOpt":
                    self.payOpt[d[1]] = d[2]
                case "payStep":
                    self.payStep.append(d[1])
                case "TAGS":
                    self.tags += d[1]
                case "CC":
                    self.compiler_compatibility.append(d[1])
                case "reqCS":
                    self.reqCS = d[1]
                case "acceptMods":
                    self.acceptMods.extend(d[1:])
                case "broken_FLAG":
                    self.broken_FLAG = True
