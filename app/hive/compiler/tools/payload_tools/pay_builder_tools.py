
from typing import Union


class PayloadBuilderTool:
    def __init__(self, payload_builder: object):
        self.pb = payload_builder

    
    def build_c_array(self, data: Union[str, bytes]) -> str:
        if isinstance(data, str):
            data = data.encode("ascii")
        code = ""
        for byte in data:
            code += f"0x{byte:02X}, "
        code = code.rstrip(", ")
        return code
    
    def encode_to_hex(self, data: Union[str, bytes]) -> str:
        if isinstance(data, str):
            data = data.encode("ascii")
        return str(data.hex())
