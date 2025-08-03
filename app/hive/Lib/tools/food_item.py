import codecs
from typing import Union

class FoodItem:
    def __init__(self, fpath: str):
        self.fpath = fpath
        self.name = None
        self.types = None
        self.info = None

        # Not used but needed
        self.system_FLAG = "[LW]"
        self.tags = ""

        
        # Data loading type.
        self.load = None

        # options
        self.options = {}

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
                case "options":
                    self.options[d[1]] = d[2]
    
    def load_list(self, data: list) -> list:
        out = []
        cut_text = self.options.get("cut")
        if cut_text:
            cut_text = int(cut_text)
            for d in data:
                if d == "" or d == "\n" or len(d) < cut_text:
                    continue
                out.append(d.rstrip("\n"))
        else:
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
    
    def load_text(self, data: list) -> str:
        return " ".join(data)
    
    def load_text_up(self, data: list) -> str:
        text = " ".join(data)
        text = text.replace("\n", " ")
        return text.title()
    
    def load_text_clean(self, data: list) -> str:
        cut_text = self.options.get("cut")
        if cut_text:
            cut_text = int(cut_text)
            text = ""
            for line in data:
                if len(line) < cut_text:
                    continue
                text += line.replace("\n", "")
        else:
            text = "".join(data)
            text = text.replace("\n", "")
        return text
    
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
            case "text":
                return self.load_text(raw)
            case "text_up":
                return self.load_text_up(raw)
            case "text_clean":
                return self.load_text_clean(raw)
            case _:
                return None

                
                