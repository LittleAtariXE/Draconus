import os
from typing import Union
from app.tools.text_formater import Texter
from .script_item import ScriptItem


class CompLibrary:
    def __init__(self, worm_constructor: object):
        self.wc = worm_constructor
        self.msg = self.wc.msg
        self.dir_comp_script = os.path.join(os.path.dirname(__file__), "comp_script")
        self.lib = {
            "comp_script" : {}
        }
        self.find_items()
    
    def find_items(self) -> None:
        c = 0
        for root, dirs, files in os.walk(self.dir_comp_script):
            for file in files:
                script = ScriptItem(os.path.join(root, file))
                self.lib["comp_script"][script.name] = script
                c += 1
        self.msg("msg", f"Scan complete. {c} compile script found")
        
    
    def get_item(self, types: str, name: str) -> Union[object, None]:
        if not types in self.lib.keys():
            self.msg("error", f"[!!] ERROR: Wrong Compiler Item Type: '{types}' [!!]")
            return None
        item = self.lib[types].get(name)
        if not item:
            self.msg("error", f"[!!] ERROR: Compiler Item: '{name}' does not exists [!!]")
            return None
        return item
