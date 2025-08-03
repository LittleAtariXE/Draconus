
from random import shuffle

class TextGenerator:
    def __init__(self, text: str):
        self.separator = "<<SEPARATOR>>"
        self.raw_text = text
        self.banned_chars = ['"', "'",]
        self.tbase = self.process()
        self.index = 0
        self.max_index = len(self.tbase) - 1
    

    def process(self) -> str:
        raw = self.raw_text.split(self.separator)
        base = []
        for b in raw:
            if b == "" or b == self.separator:
                continue
            base.append(b)
        shuffle(base)
        text = ""
        while len(base) > 0:
            text += base.pop()
        
        for bc in self.banned_chars:
            text = text.replace(bc, " ")
        text = text.replace("\n", " ")
        return text
    
    def gen(self, chars_count: int) -> str:
        chars = ""
        if (self.index + chars_count) > self.max_index:
            second = self.max_index - self.index
            chars += self.tbase[self.index:self.index + second]
            new_index = chars_count - second
            chars += self.tbase[0:new_index]
            self.index = new_index
        else:
            chars += self.tbase[self.index:self.index + chars_count]
            self.index += chars_count
        return chars


class AsmGenerator:
    def __init__(self, temp_tool: object):
        self.TT = temp_tool
    

    def format_shellcode(self, shellcode: str) -> list:
        return [int(b, 16) for b in shellcode.split(", ")]

    def build_scode(self, shellcode: str, text_data: str, var_name: str) -> str:
        gen = TextGenerator(text_data)
        scode = self.format_shellcode(shellcode)
        vcode = ""
        vall = f'{var_name}_all: dq '
        vlen = f'{var_name}_len: equ {len(scode)}\n'
        for i, b in enumerate(scode):
            value = gen.gen(b)
            vcode += f'{var_name}{i}: db "{value}",0\n'
            vall += f'{var_name}{i}, '
        vall += "0\n"
        return vcode + "\n" + vall + vlen
        


