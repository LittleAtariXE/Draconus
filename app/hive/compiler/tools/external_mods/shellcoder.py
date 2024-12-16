import os
from typing import Union
from jinja2 import Template


class MasterShellCoder:
    def __init__(self, external_modules_object: object):
        self.em = external_modules_object
        # self.msg = self.em.msg
    
    def encode_ascii(self, data: list) -> list:
        ascii_data = []
        for d in data:
            ascii_data.append("0x" + d.encode("ascii").hex())
        return ascii_data
    
    def decode_ascii(self, data: list) -> list:
        decode_data = []
        for d in data:
            decode_data.append(bytes.fromhex(d.lstrip("0x")).decode("ascii"))
        return decode_data
    
    def reverse_data(self, data: list, main_data_reverse: bool = False) -> list:
        rev_data = [d[::-1] for d in data]
        if main_data_reverse:
            return rev_data[::-1]
        else:
            return rev_data
    
    def string_find_zero(self, data_part: str) -> bool:
        """Return True if string contains '00'"""
        data = data_part[2:]
        for x in range(0, len(data), 2):
            if data[x:x+2] == "00":
                return True
        return False
    
    def shellcode_code_correct(self, code_part: str, num_bytes: int, reg: str = "b", tabs_num: int = 1) -> str:
        c_part = ""
        tab = "\t" * tabs_num
        unpack = code_part[2:]
        for x in range(0, len(unpack), 2):
            if unpack[x:x+2] != "00":
                c_part += unpack[x:x+2]
        diff = num_bytes - len(c_part) / 2
        if diff == 2 or diff == 1:
            new_code = f"{tab}mov {reg}x, 0x{c_part}\n{tab}push {reg}x\n"
        elif diff == 3:
            new_code = f"{tab}xor e{reg}x, e{reg}x\n{tab}mov {reg}l, 0x{c_part}\n{tab}push {reg}x\n"
        # elif diff == 1:
        #     new_code = f"{tab}mov {reg}l, 0x{c_part[0:2]}\n{tab}push {reg}l\n{tab}mov {reg}x, 0x{c_part[2:6]}\n{tab}push {reg}x\n"
        return new_code
        
        

    def shellcode_path(self, path: str, bytes_count: int = 4, add_char: str = "/", return_ascii: bool = True) -> list:
        data = []
        while len(path) % bytes_count != 0:
            path = add_char + path
        for n in range(0, len(path) - 1, bytes_count):
            data.append(path[n:n + bytes_count][::-1])
        data = data[::-1]
        if return_ascii:
            return self.encode_ascii(data)
        else:
            return data
    
    def shellcode_code(self, code: str, bytes_count: int = 4, add_char: str = "#", return_ascii: bool = True) -> list:
        data = []
        for n in range(0, len(code), bytes_count):
            data.append(code[n:n + bytes_count][::-1])
        if len(data[-1]) < bytes_count:
            diff = bytes_count - len(data[-1])
            data[-1] = diff * add_char + data[-1]
        data = data[::-1]
        if return_ascii:
            return self.encode_ascii(data)
        else:
            return data

    def shellcode_code_asm(self, bytes_data: list, add_cmd: str = "push ", tabs_num: int = 1, correct_code: bool = False) -> str:
        code = ""
        add_cmd = "\t" * tabs_num + add_cmd
        if correct_code:
            for b in bytes_data:
                if self.string_find_zero(b):
                    code += self.shellcode_code_correct(b, num_bytes=4)
                else:
                    code += add_cmd + b + "\n"
        else:
            for b in bytes_data:
                code += add_cmd + b + "\n"
        return code
 
