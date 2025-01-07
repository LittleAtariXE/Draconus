
import base64
from typing import Union


class PayEncoder:
    def __init__(self, payload_builder: object):
        self.pb = payload_builder
        self.format = self.pb.default_encode
        self.msg = self.pb.msg
    

    def encode_b64(self, code: Union[str, bytes], add_executor: bool = False) -> Union[str, bytes]:
        if isinstance(code, str):
            code = code.encode(self.format)
        try:
            code = base64.b64encode(code)
        except Exception as e:
            self.msg("error", f"[!!] ERROR: Encoding payload: '{e}' [!!]", sender=self.pb.name)
            return code
        if add_executor:
            code = f"exec(base64.b64decode({code}))"
        return code
    
    def encode_b64_loop(self, code: Union[str, bytes], count: int = None) -> str:
        if not count:
            count = 1
        if isinstance(code, str):
            code = code.encode(self.format)
        for _ in range(count):
            code = base64.b64encode(code)
        code = f"c={code}\ne=lambda c:base64.b64decode(c)\nfor _ in range({count}):c=e(c)\nexec(c)"
        return code

    def asm_stack_builder(self, code: Union[str, bytes], bytes_count: int = None, command: str = None) -> str:
        if not bytes_count:
            bytes_count = 4
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
    
    def encode_hex(self, code: Union[str, bytes], encode_format: str = None) -> str:
        if not encode_format:
            encode_format = self.format
        if isinstance(code, str):
            code = code.encode(encode_format)
        return str(code.hex())
    
    def encode_bin_hex(self, code: Union[str, bytes]) -> str:
        if isinstance(code, str):
            code = code.encode("ascii")
        data = ""
        for i, byte in enumerate(code):
            data += f"0x{byte:02X}"
            if i != len(code) - 1:
                data += ", "
        return data
    
