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
    
