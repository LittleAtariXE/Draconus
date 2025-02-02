import codecs
from typing import Union

class FoodItem:
    def __init__(self, fpath: str):
        self.fpath = fpath
        self.name = None
        self.types = None
        self.info = None

        # Data loading type.
        self.load = None

        self.make()


    @property
    def value(self) -> any:
        return self.load_data()

    
    def load_raw_data(self) -> list:
        data = []
        with open(self.fpath, "r") as f:
            for line in f.readlines():
                if line.startswith("#!"):
                    data.append(line.lstrip("#!").rstrip("\n"))
        return data
    
    
    def make(self) -> None:
        for data in self.load_raw_data():
            d = data.split("##")
            match d[0]:
                case "name":
                    self.name = d[1]
                case "types":
                    self.types = d[1]
                case "info":
                    self.info = d[1]
                case "load":
                    self.load = d[1]
    
    def load_list(self, data: list) -> list:
        out = []
        for d in data:
            if d == "" or d == "\n":
                continue
            out.append(d.rstrip("\n"))
        return out
    
    def load_list_tuple(self, data: list) -> list:
        out = []
        for d in data:
            if d == "" or d == "\n":
                continue
            d = d.split("#")
            out.append((d[0], d[1].rstrip("\n")))
        return out
    
    def _correct_shellcode(self, line: str) -> str:
        line = line.replace('"', '')
        line = line.replace(';', '')
        line = line.strip()
        return line
    
    def load_shellcode(self, data: list) -> str:
        skip = ["\n", " ", ""]
        raw_shell = ""
        is_raw = True
        for d in data:
            if d in skip:
                continue
            d = self._correct_shellcode(d)
            if d.startswith("0x"):
                is_raw = False
            raw_shell += d
        if is_raw:
            raw_shell = codecs.decode(raw_shell, "unicode_escape")
            shellcode = ", ".join(f"0x{byte:02x}" for byte in raw_shell.encode("latin1"))
        else:
            shellcode = raw_shell
        return shellcode
    
    def load_data(self) -> any:
        if not self.load:
            return None
        raw = []
        with open(self.fpath, "r") as file:
            for line in file.readlines():
                if line.startswith("#!"):
                    continue
                raw.append(line)
        match self.load:
            case "list":
                return self.load_list(raw)
            case "list-tuple":
                return self.load_list_tuple(raw)
            case "shellcode":
                return self.load_shellcode(raw)
            case _:
                return None

                
                