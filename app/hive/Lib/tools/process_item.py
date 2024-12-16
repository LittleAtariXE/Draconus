
from typing import Union


class ProcessItem:
    def __init__(self, fpath: str):
        self.fpath = fpath
        self.name = None
        self.types = None
        self.info = None
        self.sheme = []
        self.options = {}

        self.make()
    

    def load_headers(self) -> list:
        head = []
        with open(self.fpath, "r") as file:
            data = file.read()
        for line in data.split("\n"):
            if line.startswith("#!"):
                head.append(line.lstrip("#!").rstrip("\n"))
        return head
    
    def load_sheme(self) -> list:
        sheme = []
        with open(self.fpath, "r") as file:
            data = file.read()
        for line in data.split("\n"):
            if line.startswith("#!"):
                continue
            if line == "" or line == "\n":
                continue
            sheme.append(line.strip("[]"))
        return sheme
    
    def make(self) -> None:
        head = self.load_headers()
        for d in head:
            d = d.split("##")
            match d[0]:
                case "name":
                    self.name = d[1]
                case "types":
                    self.types = d[1]
                case "info":
                    self.info = d[1]
                case "options":
                    self.options[d[1]] = d[2]

        self.sheme = self.load_sheme()

