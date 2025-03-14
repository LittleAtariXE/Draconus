
from .payload_tools import PT_MOD_Template
from .template_tools import TT_MOD_Generator
from .dustman import TT_MOD_Dustman

from typing import Union

class MasterTempTool:
    def __init__(self, coder_payloader_wrapper: object):
        self.wrapper = coder_payloader_wrapper
        self.morpher = PT_MOD_Template(self)
        self.temp_tool = TT_MOD_Generator(self)
        self.dustman = TT_MOD_Dustman(self)

    
    def var_len(self, variable: object) -> int:
        return len(variable)
    
    def shellcode_len(self, variable: object) -> int:
        scode = variable.split(", ")
        return len(scode)
    
    def generate_text(self, src_data: list) -> str:
        return self.temp_tool.generate_text(src_data)
    
    def build_asm_scvar(self, src_data: list, shellcode: str, var_name: str, table_name: str, arch: str = "x86") -> str:
        return self.temp_tool.build_asm_var_shellcodex(src_data, shellcode, var_name, table_name, arch)
    
    def morph_garbage_code(self, code: str, num_chars: int = 1) -> str:
        return self.morpher.morph_code_garbage_char(code, num_chars)
    
    def random_text(self, data_base: Union[list, tuple, set], variable: str = None) -> str:
        if not variable or variable == "$random":
            return self.dustman.random_string(data_base)
        else:
            return variable
    
    def gen_app_version(self, separator: str = ".", number_count: str = "random") -> str:
        return self.dustman.random_version(separator, number_count)
    
    def generate_number(self, min_num: int, max_num: int) -> int:
        return self.dustman.generate_number(min_num, max_num)
    
    def asm_hex_bytes(self, text: str, add_null_bytes: bool = True) -> str:
        return self.temp_tool.asm_hex_bytes(text, add_null_bytes)
        
    