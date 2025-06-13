
from typing import Union

class TT_MOD_VarGenerator:
    def __init__(self, temp_tools: object):
        self.TT = temp_tools
    

    def nasm_gen_var(self, data: Union[list, tuple, set], var_name: str, list_name: str) -> str:
        code = ""
        lcode = f"\t{list_name}: dq"
        c = 0
        for vdata in data:
            code += f'\t{var_name}{c}: db "{vdata}", 0\n'
            lcode += f" {var_name}{c},"
            c += 1
        lcode += " 0\n"
        code = code + lcode
        return code

    def nasm_gen_hex_var(self, data: Union[list, tuple, set], var_name: str, list_name: str, hex_encode: int = 0, add_null_bytes: bool = True) -> str:
        code = ""
        lcode = f"\t{list_name}: dq"
        c = 0
        for vd in data:
            out = [f"0x{ord(one_byte)+hex_encode:02X}" for one_byte in vd]
            if add_null_bytes:
                out.append("0x00")
            out = ", ".join(out)
            code += f'\t{var_name}{c}: db {out}\n'
            lcode += f" {var_name}{c},"
            c += 1
        lcode += " 0\n"
        return code + lcode


