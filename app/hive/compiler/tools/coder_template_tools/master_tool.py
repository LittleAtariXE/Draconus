
from .payload_tools import PT_MOD_Template
from .template_tools import TT_MOD_Generator
from .dustman import TT_MOD_Dustman
from .shadow_tool import TT_MOD_Shadow
from .shadow_tool import SHADOW_DEFAULT_LAYER, SHADOW_LAYER_1
from .var_tool import TT_MOD_VarGenerator

from typing import Union

class MasterTempTool:
    def __init__(self, coder_payloader_wrapper: object):
        self.wrapper = coder_payloader_wrapper
        self.morpher = PT_MOD_Template(self)
        self.temp_tool = TT_MOD_Generator(self)
        self.dustman = TT_MOD_Dustman(self)
        self.shadow = TT_MOD_Shadow(self)
        self.var_generator = TT_MOD_VarGenerator(self)


        # Layers
        self.SHADOW_DEFAULT_LAYER = SHADOW_DEFAULT_LAYER
        self.SHADOW_LAYER_1 = SHADOW_LAYER_1

    
    def var_len(self, variable: object) -> int:
        return len(variable)
    
    def shellcode_len(self, variable: object) -> int:
        scode = variable.split(", ")
        return len(scode)
    
    def generate_text(self, src_data: list) -> str:
        return self.temp_tool.generate_text(src_data)
    
    def build_asm_scvar(self, src_data: list, shellcode: str, var_name: str, table_name: str, arch: str = "x86", add_null_byte: bool = False) -> str:
        return self.temp_tool.build_asm_var_shellcodex(src_data, shellcode, var_name, table_name, arch, add_null_byte)
    
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

    def asm_hex_encrypt_bytes(self, text: str, decrypt_bytes: int = 0, add_null_bytes: bool = True):
        # change string to hex
        # ex: 'abc' to 0x61, 0x62, 0x63
        return self.morpher.asm_hex_bytes(text, decrypt_bytes, add_null_bytes)
    
    def shadow_gen_name(self, text: str, layer: str = None) -> str:
        return self.shadow.generate_code(text, layer)

    def asm_add_code_var(self, src_data: str, var_name: str = "description", array_name: str = "text_all", decrypt_bytes: int = 0, limit_char: int = 1023) -> str:
        return self.morpher.asm_add_code_var(src_data, var_name, array_name, decrypt_bytes, limit_char)
    
    def AsmSh_make_table(self, data: str, base_chars: str = None, set_as_default: bool = False) -> dict:
        return self.shadow.make_table(data, base_chars, set_as_default)
    
    def AsmSh_encode(self, in_name: str, data: str = None, base_chars: str = None) -> str:
        return self.shadow.make_code(in_name, data, base_chars)
    
    def AsmSh_reset_table(self) -> None:
        return self.shadow.reset_default_table()
    
    def AsmSh_build_var(self, text: str, var_name: str, var_len: int = 256) -> str:
        return self.shadow.make_base_data(text, var_name, var_len)
    
    def nasm_make_var(self, data: Union[list, tuple, set], var_name: str, list_name: str) -> str:
        # Creates variables from the given data and a list containing pointers to those variables.
        return self.var_generator.nasm_gen_var(data, var_name, list_name)
    
    def nasm_make_hex_var(self, data: Union[list, tuple, set], var_name: str, list_name: str, hex_encode: int = 0, add_null_bytes: bool = True) -> str:
        # Creates encode hex variables from the given data and a list containing pointers to those variables.
        return self.var_generator.nasm_gen_hex_var(data, var_name, list_name, hex_encode, add_null_bytes)
        