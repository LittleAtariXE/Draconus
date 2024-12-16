
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
            case _:
                return None

                
                