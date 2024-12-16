import os
from jinja2 import Template
from typing import Union


class MrPattern:
    def __init__(self, external_modules_object: object):
        self.em = external_modules_object
        self.msg = self.em.msg
        self.dir_out = self.em.dir_out
        self.dir_temp = os.path.join(os.path.dirname(__file__), "templates")
        self.patterns = {
            "shellcode_C" : os.path.join(self.dir_temp, "shellcode.c")
        }
    
    def save_file(self, worm_name: str, data: str, fext: str = ".c") -> None:
        fpath = os.path.join(self.dir_out, worm_name, f"{worm_name}{fext}")
        with open(fpath, "w") as f:
            f.write(data)
        self.msg("msg", f"Save file: '{worm_name}{fext}'", sender="MrPattern")
    
    def load_file(self, fpath: str) -> str:
        with open(fpath, "r") as file:
            data = file.read()
        return data

    def render(self, worm_name: str, data: dict, pattern_name: str) -> None:
        pattern = self.patterns.get(pattern_name)
        data["PATTERN_file_name"] = worm_name
        if not pattern:
            self.msg("error", "[!!] ERROR: Unknown Pattern", sender="MrPattern")
            return
        code = Template(self.load_file(pattern))
        code = code.render(data)
        self.save_file(worm_name, code)
        
        