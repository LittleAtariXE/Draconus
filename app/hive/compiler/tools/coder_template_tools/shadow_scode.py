import os
from random import randint, choice


class SCode:
    def __init__(self, scode: str):
        self.raw_scode = scode
        self.scode = self.make_list()
        self.index = 0
        self.max_index = len(self.scode)
    
    @property
    def len(self) -> int:
        return len(self.scode)

    def make_list(self) -> list:
        sc = self.raw_scode.split(", ")
        return [sb for sb in sc]
    
    def get_byte(self) -> str:
        if self.index == self.max_index:
            return "0x00"
        sbyte = self.scode[self.index]
        self.index += 1
        return sbyte



class ShadowSC:
    def __init__(self, temp_tool: object):
        self.TT = temp_tool
        self._start_index = 2
        self.shellcode = None
    
    def build(self, text_database: list, scode: str, var_name: str, sc_bytes_num: int = 2, num_range: int = 5, start_index: int = None) -> str:
        self.shellcode = SCode(scode)
         # make index bytes
        bindex = []
        if not start_index:
            start_index = self._start_index
        bindex_i = start_index
        while len(bindex) < sc_bytes_num:
            index = randint(bindex_i, bindex_i + num_range)
            bindex.append(index)
            bindex_i += index
        
        steps = (self.shellcode.len // len(bindex)) + 1
        code = []
        for _ in range(steps):
            raw = choice(text_database)
            line = self.build_line(raw, bindex)
            line = f'db "{line}"'
            code.append(line)
        
        # build var index
        var_index = f'{var_name}_index: dd '
        for i in bindex:
            var_index += f"{i}, "
        var_index += "0\n"


        # build var
        vcode = ""
        vcode_all = f'{var_name}_all: dq '
        for i, line in enumerate(code):
            vcode += f'{var_name}_{i}: {line}, 0\n'
            vcode_all += f'{var_name}_{i}, '
        vcode_all += "0\n"
        vcode = vcode + "\n" + vcode_all + "\n" + var_index
        return vcode

    def build_line(self, line: str, bytes_index: list) -> str:
        nline = ""
        index = 0
        for i, c in enumerate(list(line)):
            if index == len(bytes_index):
                nline += c
                continue
            if i == bytes_index[index]:
                nline += f'", {self.shellcode.get_byte()}, "'
                index += 1
            else:
                nline += c
        return nline



