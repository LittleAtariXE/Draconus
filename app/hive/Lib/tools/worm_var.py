import base64
import ast
from typing import Union

class VarTools:
    def encode_b64(data: Union[str, bytes, int]) -> bytes:
        if isinstance(data, int):
            data = str(data)
        if isinstance(data, str):
            data = data.encode("utf-8")
        return base64.b64encode(data)

    def stack_builder(code: str, bytes_count: int = 4, command: str = None) -> str:
        if not command or command == "":
            code = code
        else:
            code = f"{command} {code}"
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
    
    def increase_value(value: Union[str, int], count: Union[str, int]) -> int:
        try:
            value = int(value)
            count = int(count)
        except ValueError:
            return 0
        return value * count

class WormVar:
    def __init__(self,
                    name: str,
                    value: any = None,
                    info: str = None,
                    types: str = "str",
                    owner_module: str = None,
                    options: dict = {},
                    force_types_FLAG: str = None):

        self.__store_first_value = value
        self.name = name
        self.__value = value
        self.info = info
        self.types = types
        self.owner = owner_module
        self.options = options
        self.force_types_FLAG = force_types_FLAG
        self.no_value = "<NO_VALUE>"
        self.show_limit = 22
        if not value:
            self.reqVar_FLAG = True
        else:
            self.reqVar_FLAG = False

    @property
    def value(self) -> any:
        if self.reqVar_FLAG:
            return None
        value = self.correct_types()
        value = self.check_options(value)
        return value
    
    @property
    def raw_value(self) -> any:
        if self.reqVar_FLAG:
            return None
        return self.__value


    def correct_types(self) -> any:
        if self.force_types_FLAG:
            types = self.force_types_FLAG
        else:
            types = self.types

        match types:
            case "str":
                return self.__value
            case "int":
                return self.convert_to_int(self.__value)
            case _:
                return self.convert_to(self.__value)
    
    def check_options(self, value: any) -> any:
        increase = self.options.get("INCREASE")
        if increase:
            value = VarTools.increase_value(value, increase)
        if self.options.get("ENCODE_B64"):
            return VarTools.encode_b64(value)
        elif self.options.get("STACK_BUILD"):
            bytes_num = self.options.get("STACK_BYTES", 4)
            command = self.options.get("STACK_COMMAND")
            return VarTools.stack_builder(value, bytes_num, command)
        else:
            return value
    
    def convert_to_int(self, value: str) -> Union[str, int]:
        try:
            return int(value)
        except ValueError:
            return value
    
    def convert_to(self, value: any) -> any:
        try:
            out = ast.literal_eval(value)
            return out
        except Exception as e:
            print("E: ", e)
            return value

    def set_value(self, value: any) -> None:
        self.__value = value
        self.reqVar_FLAG = False
    
    def reset(self) -> None:
        self.__value = None
        self.reqVar_FLAG = True
    
    def restore(self) -> None:
        self.__value = self.__store_first_value
        self.reqVar_FLAG = False
    
    def show(self) -> str:
        if not self.__value:
            return self.no_value
        if len(str(self.__value)) > self.show_limit:
            return f"{str(self.__value)[0:self.show_limit]}..."
        else:
            return str(self.__value)

    
    def __repr__(self) -> any:
        return str(self.value) if self.value else self.no_value
    
