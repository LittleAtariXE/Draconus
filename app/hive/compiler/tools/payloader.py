import os
import base64
from typing import Union
from jinja2 import Template

class Payloader:
    def __init__(self, queen: object, coder: object):
        self.queen = queen
        self.msg = self.queen.msg
        self.coder = coder
    
    def load_bin(self, fpath: str) -> bytes:
        with open(fpath, "rb") as file:
            data = file.read()
        return data
    
    def encode(self, types: str, data: Union[bytes, str]) -> Union[bytes, str]:
        match types:
            case "base64":
                return base64.b64encode(data).decode("utf-8")
            case _:
                self.msg("error", f"[!!] ERROR: Unknown Payload Encode: '{types}' [!!]")
                return data
    
    def encode_str(self, data: Union[bytes, str], types: str = "base64") -> str:
        if not types:
            return data
        if isinstance(data, str):
            data = data.encode("utf-8")
    
        match types:
            case "base64":
                return base64.b64encode(data)
            case "bytes_hex":
                return data.hex()
            case _:
                self.msg("error", f"[!!] ERROR: Unknown Payload Encode: '{types}' [!!]")
                return data
                
    def stack_builder(self, code: str, bytes_count: int = 4, command: str = None) -> str:
        if not command or command == "":
            code = code
        else:
            command = command.split("$")
            if len(command) == 1:
                code = f"{command[0]} {code}"
            else:
                code = f"{command[0]}{code}{command[1]}"
        str_data = []
        for n in range(0, len(code), bytes_count):
            str_data.append(code[n:n + bytes_count][::-1])
        str_data = str_data[::-1]
        ascii_data = []
        for sd in str_data:
            ascii_data.append(sd.encode("ascii").hex())
        while len(ascii_data[0]) < bytes_count * 2:
            ascii_data[0] = f"00{ascii_data[0]}"
        stack_data = []
        for ad in ascii_data:
            stack_data.append(f"0x{ad}")
        asm_code = ""
        for sd in stack_data:
            asm_code += f"push dword {sd}\n"
        return asm_code
    
    def raw_bin(self, fpath) -> bytes:
        return self.encode("base64", self.load_bin(fpath))
    
    def get_options(self, name: str, payload_opt: dict) -> dict:
        opt = payload_opt.get(name)
        if not opt:
            opt = {}
        return opt
    
    def encode_code(self, data: str, var: dict, name: str, types: str = "base64", count : Union[str, int, None] = 1) -> str:
        if not count:
            count = 1
        try:
            count = int(count)
        except ValueError as e:
            self.msg("error", f"[!!] ERROR Payload encode count: '{e}' [!!]")
            return data
        for _ in range(count):
            data = self.encode_str(data, types)
        var[f"{name}_ENCODE_COUNT"] = count
        return data

    def bin_convert_bytes(self, bin_data: bytes, var: dict) -> str:
        data = ""
        for i, byte in enumerate(bin_data):
            data += f"0x{byte:02X}"
            if i != len(bin_data) - 1:
                data += ", "
        var["EXE_LEN"] = len(bin_data)
        return data
        
    def prepare_binary(self, mod: object, var: dict, payload_options: dict = {}) -> bytes:
        bin_data = self.load_bin(mod.binary)
        encode = payload_options.get("ENCODE")
        if encode:
            match encode:
                case "convert_bytes":
                    return self.bin_convert_bytes(bin_data, var)
                case "base64":
                    return self.encode_str(bin_data, "base64")
        else:
            return bin_data
    
    def add_py_loader(self, mod: object, var: dict, payload_options: dict = {}) -> str:
        imports = self.coder.return_imports(mod.raw_code)
        code = f"""def loader():
    import sys, subprocess\n
    for i in {imports}:
        try:
            exec(i)
        except ModuleNotFoundError:
            i = i.split(" ")[1]
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", i])
            except:
                pass
loader()
{mod.raw_code}"""
        return code



    
    def prepare(self, mod: object, raw_var: dict, name: str, payload_options: dict = {}) -> Union[str, bytes]:
        if mod.binary:
            return self.prepare_binary(mod, raw_var, payload_options)
        code = mod.raw_code
        if payload_options.get("INCLUDE_IMPORTS") or mod.import_FLAG:
            code = self.coder.return_code(code, return_imports=True)
            code = self.coder.render_single_str(code, raw_var)
        else:
            code = self.coder.render_single(code, raw_var)
        pyloader = payload_options.get("PY_LOADER")
        if pyloader == True or pyloader == "True":
            code = self.add_py_loader(mod, raw_var, payload_options)
            
        encode = payload_options.get("ENCODE")
        if encode:
            code = self.encode_code(code, raw_var, name, encode, payload_options.get("ENCODE_COUNT"))
        if payload_options.get("STACK_BUILD"):
            bytes_num = payload_options.get("STACK_BYTES", 4)
            command = payload_options.get("STACK_COMMAND")
            code = self.stack_builder(code, bytes_num, command)
        return code
        
        
       

        