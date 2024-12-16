import os
import base64

from .shadows.digdug import DigDug

class FairyTale:
    def __init__(self, code: str):
        self.code = code
    
    def reverse_and_decrement(self, byte_array):
        counter = 0
        while counter < 3:
            temp_array = byte_array.copy()
            for i in range(len(byte_array)):
                temp_array[i] = byte_array[len(byte_array) - i - 1] - 3
            byte_array = temp_array
            counter += 1
        return byte_array
    
    def obfuscate(self) -> str:
        code = bytearray(self.code, "utf-8")
        code = self.reverse_and_decrement(code)
        code = code.decode("utf-8")
        return f"""import os
def obfuscate_code(byte_code):
    counter = 9
    while counter > 6:
        temp_byte_code = byte_code.copy()
        for i in range(len(byte_code)):
            temp_byte_code[i] = byte_code[len(byte_code) - i - 1] + 3
        byte_code = temp_byte_code
        counter -= 1
    return byte_code
code_str = r""\"{code}\"""
byte_code_array = bytearray(code_str, "utf-8")
obfuscated_byte_code = obfuscate_code(byte_code_array)
decoded_code = obfuscated_byte_code.decode("utf-8")
eval(compile(decoded_code, '<string>', 'exec'))"""




class BaseOneLine:
    def __init__(self, code: str):
        self.code = base64.b64encode(code.encode("utf-8"))
    
    def shadow(self) -> str:
        return  f"""\nimport base64\nexec(base64.b64decode({self.code}).decode("utf-8"))"""

class Shadow:
    def __init__(self, coder: object):
        self.coder = coder
        self.msg = self.coder.msg
    
    def use(self, worm_pipeline: object, shadow: object) -> object:
        match shadow.name:
            case "BaseOneLine":
                shadow = BaseOneLine(worm_pipeline.code)
                worm_pipeline.code = shadow.shadow()
                self.msg("msg", "Obfuscate code complete")
            case "FairyTale":
                shadow = FairyTale(worm_pipeline.code)
                worm_pipeline.code = shadow.obfuscate()
                self.msg("msg", "Obfuscate code complete")
            case "DigDug":
                shadow = DigDug()
                self.msg("msg", "Start hiding code.")
                worm_pipeline.code = shadow.shadow(worm_pipeline.code, worm_pipeline.var)
                self.msg("msg", "Obfuscate code complete")
            case _:
                self.msg("error", "[!!] Unknown obfuscate method [!!]")

        return worm_pipeline
