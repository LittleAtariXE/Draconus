from typing import Union

class Shellcoder:
    def __init__(self, raw_scode: str):
        self.raw = raw_scode

    def _format(self, in_scode: str) -> str:
        return in_scode
    
    def convert2int(self, in_scode: str) -> Union[list, None]:
        scode = in_scode.split(", ")
        try:
            sc = [int(b, 16) for b in scode]
            return sc
        except:
            return None
        


class BytesHide:
    def __init__(self, master_tool: object):
        self.MT = master_tool
        
    def single_char_generator(self, raw_scode: str, char: str = "#", last_char: str = "0", separator: str = ",", new_line: bool = True) -> str:
        if new_line:
            new_line = "\n"
        else:
            new_line = ""
        sc = Shellcoder(raw_scode)
        sc_int = sc.convert2int(sc.raw)
        out = ""
        for b in sc_int:
            line = f'"{char*b}"{separator}{new_line}'
            out += line
        out += f'"{last_char}"{new_line}'
        return out
            



    