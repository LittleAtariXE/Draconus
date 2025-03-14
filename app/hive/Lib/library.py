import os
import json
from typing import Union

from .tools.lib_item import LibItem as LibraryItem
from .tools.food_item import FoodItem
from .tools.process_item import ProcessItem
from app.tools.text_formater import Texter

LIBRARY_ITEMS = os.path.join(os.path.dirname(__file__), "items")




    
class Library:
    def __init__(self, queen: object, items_dir: str = LIBRARY_ITEMS):
        self.queen = queen
        self.msg = self.queen.msg
        self.dir_items = items_dir
        self.dir_food = os.path.join(self.dir_items, "food")
        self.dir_process = os.path.join(self.dir_items, "process")
        self.dir_comp_script = os.path.join(self.dir_items, "comp_script")
        self.dir_icons = os.path.join(os.path.dirname(__file__), "icons")
        self.lib = {
            "worm" : {},
            "support": {},
            "module" : {},
            "payload" : {},
            "starter" : {},
            "shadow" : {},
            "junk" : {},
            "wrapper" : {},
            "food" : {},
            "process": {},
            "cscript": {}
        }
        self.shadow = {}
        self.find_items()

        self.texter = Texter(25, 100)
        
    
    @property
    def lib_data(self) -> dict:
        return self.lib["data"]

    def find_items(self) -> None:
        c = 0
        for root, dirs, files in os.walk(self.dir_items):
            if "binary" in root or "food" in root or "process" in root or "comp_script" in root:
                continue
            for name in files:
                path = os.path.join(root, name)
                item = LibraryItem(path)
                if item.types in self.lib.keys():
                    self.lib[item.types][item.name] = item
                    c += 1
        ##### FOOD #######
        for item in os.listdir(self.dir_food):
            food = FoodItem(os.path.join(self.dir_food, item))
            self.lib["food"][food.name] = food
        ### Process Items ####
        for item in os.listdir(self.dir_process):
            proc = ProcessItem(os.path.join(self.dir_process, item))
            self.lib["process"][proc.name] = proc
        ### Compiler Script ###
        for item in os.listdir(self.dir_comp_script):
            cs = LibraryItem(os.path.join(self.dir_comp_script, item))
            self.lib["cscript"][cs.name] = cs
            
        

    
        self.queen.msg("msg", f"Scan complete. {c} items found")

    def get_item(self, types: str, name: str, no_output: bool = False) -> Union[object, None]:
        typ = self.lib.get(types)
        if not typ:
            if not no_output:
                self.queen.msg("error", f"[!!] ERROR: Item type: {typ} not exists [!!]")
            return None
        mod = typ.get(name)
        if not mod:
            if not no_output:
                self.queen.msg("error", f"[!!] ERROR: Item name: {name} not exists [!!]")
            return None
        return mod
 
    def get_lib_data(self, name: str) -> Union[object, None]:
        data = self.lib_data.get(name)
        if not data:
            self.msg("error", f"[!!] No '{name}' in library data [!!]")
            return None
        return data
    
    def get_shadow(self, name: str) -> Union[object, None]:
        shadow = self.lib["shadow"].get(name)
        if not shadow:
            self.msg("error", f"[!!] Obfuscator: '{name}' does not exists")
            return None
        return shadow

    
    
    def show_items(self, types: str) -> None:
        items = self.lib.get(types)
        if not items:
            self.msg("error", f"Items: '{types}' is not in the library")
            return
        text = "\n" + "-" * 30 + f" {types} " + "-" * 30 + "\n"
        for item in items.values():
            text += self.texter.make_2column(item.name, item.info)
            text += "\n"
            text += "- " * 70 + "\n"
        self.msg("msg", text)
    
    def show_process_worm(self) -> None:
        text = "\n" + "#" * 50 + " Process Items " + "#" * 50 + "\n"
        text += "-" * 120 + "\n"
        text += "-" * 50 + " Despcription " + "-" * 50 + "\n"
        text += self.texter.make_2column("-- [BASE] --", "Creates the worm's basic code.")
        text += "\n"
        text += self.texter.make_2column("-- [SHADOW] --", "It obfuscates the code with modules.")
        text += "\n"
        text += self.texter.make_2column("-- [STARTER] --", "It creates a starter and puts the code in it.")
        text += "\n"
        text += self.texter.make_2column("-- [ADD_IMPORTS] --", "Adds imported libraries to the code.")
        text += "\n"
        text += self.texter.make_2column("-- [WRAPPER] --", "It places the worm code in other code.")
        text += "\n"
        text += self.texter.make_2column("-- [SAVE_RAW] --", "Saves the worm code to a file.")
        text += "\n"
        text += self.texter.make_2column("-- [COMPILER] --", "Run the compiler and compile the worm.")
        text += "\n"
        text += self.texter.make_2column("-- [SHOW_OP_CODE] --", "Creating a shellcode and displaying it on the screen.")
        text += "\n"
        text += self.texter.make_2column("-- [BUILD_C_SCODE] --", "It creates a C language file and puts the shellcode there. The file is ready for compilation.")
        text += "\n"
        text += self.texter.make_2column("-- [BASE_SHELL] --", "It uses additional modules to create code.")
        text += "\n"
        text += self.texter.make_2column("-- [CODE_LOADER] --", "Adds code before the worm is launched.")
        text += "\n"
        
        for name, obj in self.lib["process"].items():
            text += "-" * 120 + "\n"
            text += self.texter.make_2column("-- Name", name)
            text += "\n"
            text += self.texter.make_2column("-- Description", obj.info)
            text += "\n"
            sheme = f"[{obj.sheme[0]}]"
            for s in obj.sheme[1:]:
                sheme += f" --> [{s}]"
            text += self.texter.make_2column("-- Process Sheme", sheme)
            text += "\n"
        self.msg("msg", text)
                