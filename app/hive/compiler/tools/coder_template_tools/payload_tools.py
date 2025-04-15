import string
from typing import Union
from random import randint

class PT_MOD_Template:
    def __init__(self, temp_tools: object):
        self.TT = temp_tools
        self.chars = string.ascii_letters + string.digits
    
    def generate_chars(self, num: int = 1) -> str:
        chars = ""
        while len(chars) < num:
            c = self.chars[randint(0, len(self.chars) - 1)]
            chars += c
        return chars
    
    def morph_code_garbage_char(self, data: str, num_chars: int = 1) -> str:
        # data input: 0x01, 0xa3, 0xbb etc.
        code = ""
        for d in data.split(","):
            d = d.replace(",", "").replace("0x", "").strip()
            code += f"{self.generate_chars()}{d}"
        return code
    
    def asm_hex_bytes(self, src_data: str, decyrpt_bytes: int = 0, add_null_bytes: bool = True) -> str:
        out = [f"0x{ord(one_byte)+decyrpt_bytes:02X}" for one_byte in src_data]
        if add_null_bytes:
            out.append("0x00")
        return ", ".join(out)
    
    def asm_add_code_var(self, src_data: str, var_name: str = "description", array_name: str = "text_all", decrypt_bytes: int = 0, limit_char: int = 1023) -> str:
        data = [src_data[d:d+limit_char] for d in range(0, len(src_data), limit_char)]
        code = ""
        array = f"{array_name}: dq "
        for i, d in enumerate(data):
            code += f"{var_name}{i}: db {self.asm_hex_bytes(d, decrypt_bytes)}\n"
            array += f"{var_name}{i}, "
        return code + array + "0\n"


