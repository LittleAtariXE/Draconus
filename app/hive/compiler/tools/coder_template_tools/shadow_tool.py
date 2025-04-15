import string
from random import choice
from typing import Union

SHADOW_DEFAULT_LAYER = "#" + string.ascii_letters +  "." + "_" + "1234567890"
SHADOW_LAYER_1 = "#" + SHADOW_DEFAULT_LAYER + string.ascii_letters + string.ascii_letters + "." + "_" + SHADOW_DEFAULT_LAYER

class TT_MOD_Shadow:
    def __init__(self, temp_tool: object):
        self.TT = temp_tool
    

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



