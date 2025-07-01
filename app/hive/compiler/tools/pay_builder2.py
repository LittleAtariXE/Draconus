import os
from jinja2 import Template
from typing import Union, Tuple

from .payload_tools.pay_encoder import PayEncoder
from .payload_tools.pay_tools import PayloadTools
from .coder_template_tools.master_tool import MasterTempTool
from .payload_tools.pay_builder_tools import PayloadBuilderTool



class PayloadObject:
    def __init__(self, payload_module: object, var_name_payload: str, variables: dict = {}, worm_step_payload: list = [], options: dict = {}):
        self.payload_mod = payload_module
        self.var_name = var_name_payload
        self.pay_step_from_owner = worm_step_payload
        self.pay_step = []
        self.owner_options = options
        self.options = {}
        self.owner = self.payload_mod.owner
        self.var = variables

        self._read_payload_data()

        self.bin_data = self.payload_mod.binary
              
        self._build()
        self._code = None

    

    @property
    def render_FLAG(self) -> str:
        return str(self.options.get("render_FLAG"))


    @property
    def code(self) -> Union[str, bytes]:
        if not self._code:
            return self.raw_code
        else:
            return self._code



    def _read_payload_data(self) -> None:
        # default options
        self.options["render_FLAG"] = "True"

        # first. update data from payload module
        data = self.payload_mod.payload_object.get(self.payload_mod.name)
        if data:
            self.options.update(data.options)
            self.pay_step.extend(data.work_step)

        # update data from owner module
        self.options.update(self.owner_options)
        self.pay_step.extend(self.pay_step_from_owner)

    
    def _build(self) -> None:
        if self.bin_data:
            self.raw_code = self.payload_mod.bin_code
        else:
            self.raw_code = self.payload_mod.raw_code
        
       


class PayloadBuilder2:
    def __init__(self, queen: object, coder: object):
        self.name = "PayloadBuilder"
        self.queen = queen
        self.coder = coder
        self.msg = self.queen.msg
        self.default_encode = self.queen.conf.payload_default_encode
        self.PE = PayEncoder(self)
        self.PT = PayloadTools(self)
        self.TempTool = MasterTempTool(self)
        self.PBT = PayloadBuilderTool(self)

        # default render function
        self.render = self.coder.render_single_template

    

    def process(self, payload_module: object, var_payload_name: str, owner_module: object, var: dict = {}) -> str:
        # check for payload options from owner module
        owner_data = owner_module.payload_object.get(var_payload_name)
        if owner_data:
            owner_step = owner_data.work_step
            owner_opt = owner_data.options
        else:
            owner_step = []
            owner_opt = {}
        self.msg("msg", f"Building payload: '{payload_module.name}' ......", sender=self.name)
        pay = PayloadObject(payload_module, var_payload_name, var, owner_step, owner_opt)
        process_step = self.prepare_step(pay)
        for ps in process_step:
            self.msg("dev", f"Payload process step: {ps.__name__}", sender=self.name)
            pay = ps(pay)
        
        self.msg("msg", f"Builiding payload '{payload_module.name}' complete.", sender=self.name)
        return pay.code
    
    def prepare_step(self, payload: object) -> list:
        process_step = []
        for ps in payload.pay_step:
            self.add_proc_step(ps, process_step)
        # check for render
        if not "return_code" in payload.pay_step:
            self.add_proc_step("return_code", process_step)
        return process_step
    
    def add_proc_step(self, step_name: str, process_step: list) -> list:
        match step_name:
            case "encode_b64":
                process_step.append(self.step_encode_b64)
            case "return_code":
                process_step.append(self.step_return_code)
            case "build_c_array":
                process_step.append(self.step_build_c_array)
            case "encode_to_hex":
                process_step.append(self.step_encode_to_hex)
            case _:
                process_step.append(self.empty_step)
        return process_step
    
    def step_return_code(self, payload: object) -> object:
        # return final code. 
        if payload.render_FLAG == "True":
            self.msg("dev", "Rendering payload code", sender=self.name)
            code = self.render(payload.code, payload.var)
        else:
            code = payload.code
        payload._code = code
        return payload
    
    def step_encode_b64(self, payload: object) -> object:
        return payload
    
    def step_build_c_array(self, payload: object) -> object:
        payload._code = self.PBT.build_c_array(payload.code)
        return payload
    
    def step_encode_to_hex(self, payload: object) -> object:
        payload._code = self.PBT.encode_to_hex(payload.code)
        return payload
    
    def empty_step(self, payload: object) -> object:
        return payload


