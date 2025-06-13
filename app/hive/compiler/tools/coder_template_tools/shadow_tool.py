import string
from random import choice
from typing import Union

SHADOW_DEFAULT_LAYER = "#" + string.ascii_letters +  "." + "_" + "1234567890"
SHADOW_LAYER_1 = "#" + SHADOW_DEFAULT_LAYER + string.ascii_letters + string.ascii_letters + "." + "_" + SHADOW_DEFAULT_LAYER

class TT_MOD_Shadow:
    def __init__(self, temp_tool: object):
        self.TT = temp_tool
        self.default_table = None
    
    def reset_default_table(self) -> None:
        self.default_table = None

    def make_char_list(self, data: str = SHADOW_LAYER_1) -> dict:
        chars = {}
        for c in SHADOW_DEFAULT_LAYER:
            chars[c] = []
        base = list(data)
        for index, char in enumerate(base):
            if not char in chars.keys():
                continue
            chars[char].append(index)
        return chars

    def generate_code(self, code_data: str, layer: str = None) -> str:
        if not layer:
            layer = SHADOW_DEFAULT_LAYER
        table = self.make_char_list(layer)
        code = []
        for c in code_data:
            if not c in table.keys():
                continue
            code.append(str(choice(table[c])))
        code.append("0")
        return ", ".join(code)
    
    def make_table(self, data: str, base_chars: str = None, set_as_default: bool = False) -> dict:
        if not base_chars:
            base_chars = string.ascii_letters + string.digits + "." + "_"
        chars = {}
        for char in base_chars:
            chars[char] = []
        base = list(data)
        for index, char in enumerate(base):
            if not char in chars.keys():
                continue
            chars[char].append(index)
        if set_as_default:
            self.default_table = chars
        return chars
    
    def make_code(self, in_name: str, data: str = None, base_chars: str = None) -> str:
        if not data and not self.default_table:
            return "0"
        if not data and self.default_table:
            table = self.default_table
        else:
            table = self.make_table(data, base_chars)
        code = []
        for c in in_name:
            if not c in table.keys():
                continue
            code.append(str(choice(table[c])))
        code.append("0")
        return ", ".join(code)
    
    def make_base_data(self, text: str, var_name: str, var_len: int = 256) -> str:
        data = [text[i:i+var_len] for i in range(0, len(text), var_len)]
        vcode = ""
        scode = f"{var_name}_all: dq"
        for i, d in enumerate(data):
            vcode += f'{var_name}{i}: db "{d}", 0\n'
            scode += f' {var_name}{i},'
        scode += " 0"
        code = vcode + "\n" + scode + "\n"
        return code
