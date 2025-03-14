
from random import randint
from typing import Union


class TT_MOD_Generator:
    def __init__(self, temp_tools: object):
        self.TT = temp_tools
    

    def generate_text(self, src_data: list) -> str:
        max_r = len(src_data) - 1
        text = src_data[randint(0, max_r)]
        return text
    
    def build_asm_var_shellcode(self, src_data: list, shellcode: Union[str, bytes], var_name: str, table_name: str) -> str:
        raw = shellcode.split(", ")
        sc_len = len(raw)
        code = ""
        table = f"{table_name}: dd "
        for i, sb in enumerate(raw):
            code += f'{var_name}{i}: db "{self.generate_text(src_data)}", 10, {sb}, 0\n'
            table += f"{var_name}{i}, "
        
        code += "\n" + table[0:-2]
        return code
    
    def build_asm_var_shellcodex(self, src_data: list, shellcode: str, var_name: str, table_name: str, arch: str = "x86") -> str:
        if arch == "x64":
            arch = "dq"
        else:
            arch = "dd"
        raw = shellcode.split(", ")
        sc_len = len(raw)
        code = ""
        table = f"{table_name}: {arch} "
        for i, sb in enumerate(raw):
            code += f'{var_name}{i}: db "{self.generate_text(src_data)}", 10, {sb}, 0\n'
            table += f"{var_name}{i}, "
        
        code += "\n" + table[0:-2]
        return code
    
    def asm_hex_bytes(self, src_data: str, add_null_bytes: bool = True) -> str:
        out = [f"0x{ord(one_byte):02X}" for one_byte in src_data]
        if add_null_bytes:
            out.append("0x00")
        return ", ".join(out)