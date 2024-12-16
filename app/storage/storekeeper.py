import os
import string
from random import randint
from typing import Union

class Storekeeper:
    def __init__(self, draco: object):
        self.draco = draco
        self.msg = self.draco.msg
        self.config = self.draco.config
        self.dir_loot_main = os.path.join(self.config.dir_output, "LOOT")
        self.dir_loot_dump = os.path.join(self.dir_loot_main, "dump")
        self.make_dirs()

    
    def make_dirs(self) -> None:
        if not os.path.exists(self.dir_loot_main):
            os.mkdir(self.dir_loot_main)
        if not os.path.exists(self.dir_loot_dump):
            os.mkdir(self.dir_loot_dump)
    

    def generate_name(self, char_len: int = 20, optional_info: str = None):
        name = ""
        chars = string.ascii_letters
        while len(name) < char_len:
            char = chars[randint(0, len(chars) - 1)]
            name += char
        if optional_info:
            return name + "#" + optional_info
        return name
    
    def prepare_warehouse(self, file_name: str) -> str:
        warehouse = os.path.join(self.dir_loot_dump, file_name)
        if not os.path.exists(warehouse):
            os.mkdir(warehouse)
        return warehouse
    
    def info_card(self, fpath: str, text: str = "") -> None:
        fpath = os.path.join(fpath, "INFO_CARD.txt")   
        try:
            with open(fpath, "a+") as file:
                file.write("\n" + "-" * 100 + "\n")
                file.write(text)
                file.write("\n\n")
        except Exception as e:
            print("ERROR: ", e)
    
    def save_loot(self, fpath: str, data: Union[bytes, str], handler_client: object, file_name: str = "") -> None:
        try:
            with open(fpath, "wb") as file:
                file.write(data)
            self.msg("msg", f"Download and save file: {file_name} successfull", sender=handler_client.client)
        except Exception as e:
            self.msg("error", f"[!!] ERROR: Save file from client: {e} [!!]", sender=handler_client.client)

    
    def take_delivery(self, data: bytes, file_name: str = None, handler: object = None, info: str = None, file_ext: str = None, file_name_extra: str = None) -> None:
        if not file_name:
            file_name = self.generate_name(optional_info=file_name_extra)
        if info:
            fpath = self.prepare_warehouse(file_name)
            self.info_card(fpath, info)
        else:
            fpath = self.dir_loot_dump
        if file_ext:
            fpath = os.path.join(fpath, f"{file_name}.{file_ext.lstrip('.')}")
        else:
            fpath = os.path.join(fpath, file_name)
        self.save_loot(fpath, data, handler, file_name)

        
        
        
            
            
            
        




        
