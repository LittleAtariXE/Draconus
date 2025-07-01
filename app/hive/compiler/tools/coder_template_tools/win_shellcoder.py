
from typing import Union


class WinShell:
    def __init__(self, temp_tools: object):
        self.TT = temp_tools
    

    def stack_build(self, code: str, bytes_len: int = 4, loader: str = None, loader_char: str = "$", add_null_terminator: bool = True, add_tabulate: int = 1) -> tuple:
        # loader need '$'
        if loader:
            code = loader.replace(loader_char, code)
        tab = ""
        for _ in range(add_tabulate):
            tab += "\t"
        data = []
        for n in range(0, len(code), bytes_len):
            data.append(code[n:n+bytes_len][::-1])
        ascii_data = []
        for d in reversed(data):
            ascii_data.append(d.encode("ascii").hex())
        if len(ascii_data[0]) == bytes_len * 2 and add_null_terminator:
            ascii_data.insert(0, "00")
        while len(ascii_data[0]) < bytes_len * 2:
            ascii_data[0] = "00" + ascii_data[0]
        # shadow space
        ss_exit = len(ascii_data) * 8
        if ss_exit & 8 == 0:
            ss_enter = 40
        else:
            ss_enter = 48
        ss_exit += ss_enter
        code = ""
        for line in ascii_data:
            code += f"{tab}push 0x{line}\n"
        # return: code, shadow space enter, shadow space exit
        return (code, ss_enter, ss_exit)
    
    def stack_build2(self, code: str, bytes_len: int = 4, shadow_space_enter: int = 40, loader: str = None, loader_char: str = "$", add_null_terminator: bool = True, add_tabulate: int = 1) -> tuple:
        # loader need '$'
        if loader:
            code = loader.replace(loader_char, code)
        print(code)
        tab = ""
        for _ in range(add_tabulate):
            tab += "\t"
        data = []
        for n in range(0, len(code), bytes_len):
            data.append(code[n:n+bytes_len][::-1])
        ascii_data = []
        for d in reversed(data):
            ascii_data.append(d.encode("ascii").hex())
        if len(ascii_data[0]) == bytes_len * 2 and add_null_terminator:
            ascii_data.insert(0, "00")
        while len(ascii_data[0]) < bytes_len * 2:
            ascii_data[0] = "00" + ascii_data[0]
        # shadow space
        ss_exit = len(ascii_data) * 8
        if ss_exit & 8 == 0:
            ss_enter = shadow_space_enter
        else:
            ss_enter = shadow_space_enter + 8
        ss_exit += ss_enter
        code = ""
        for line in ascii_data:
            code += f"{tab}push 0x{line}\n"
        # return: code, shadow space enter, shadow space exit
        return (code, ss_enter, ss_exit)

# code = "print('hello')"
# load = "cmd.exe /C python -c $"
# ws = WinShell("")
# asm = ws.stack_build(code, loader=load)
# print(asm[0])
# print(asm[1])
# print(asm[2])