import os
import tarfile
import shutil
from typing import Union



class DLC:
    def __init__(self, library: object):
        self.name = "DRACO_DLC"
        self.lib = library
        self.msg = self.lib.msg
        self.dir_items = self.lib.dir_items
        self.dir_in = self.lib.queen.conf.dir_in
        self.dir_temp = os.path.join(self.dir_in, "temp")
        self.dlc_name = self.lib.queen.conf.dlc_name
        self.dlc_conf_ext = ".conf"
        self.mod_count = 0
        self.items_path = {
            "worm" : os.path.join(self.dir_items, "worms"),
            "support" : os.path.join(self.dir_items, "support"),
            "module" : os.path.join(self.dir_items, "modules"),
            "starter" : os.path.join(self.dir_items, "starter"),
            "shadow" : os.path.join(self.dir_items, "shadow"),
            "process" : os.path.join(self.dir_items, "process"),
            "payload" : os.path.join(self.dir_items, "payloads"),
            "food" : os.path.join(self.dir_items, "food"),
            "binary" : os.path.join(self.dir_items, "binary"),
            "wrapper" : os.path.join(self.dir_items, "wrapper"),
            "garbage" : os.path.join(self.dir_items, "garbage")
        }
    
    def unpack(self, file_name: str) -> bool:
        if not os.path.exists(self.dir_temp):
            os.mkdir(self.dir_temp)
        fname = os.path.splitext(file_name)
        fpath = os.path.join(self.dir_in, file_name)
        try:
            with tarfile.open(fpath, "r") as tar:
                tar.extractall(path=self.dir_temp)
        except Exception as e:
            self.msg("error", f"[!!] ERROR Extract DLC: {e} [!!]", sender=self.name)
            return False
        return True
    
    def _read_conf(self, fpath: str) -> dict:
        conf = {}
        try:
            with open(fpath, "r") as file:
                for line in file.readlines():
                    if line == "" or line == "\n":
                        continue
                    l = line.split(":")
                    conf[l[0]] = l[1].rstrip("\n")
        except Exception as e:
            self.msg("error", f"[!!] ERROR Read config DLC: {e} [!!]", sender=self.name)
        return conf


    def read_config(self, file_list: list) -> Union[dict, None]:
        config = {}
        for file in file_list:
            f = os.path.splitext(file)
            if f[1] == self.dlc_conf_ext:
                conf = self._read_conf(file)
                config.update(conf)
        return config
    
    def correct_config(self, config: dict, mods_list: list) -> dict:
        new_conf = {}
        for mod in mods_list:
            if os.path.splitext(mod)[1] == self.dlc_conf_ext:
                continue
            types = config.get(os.path.basename(mod))
            if not types:
                continue
            new_conf[mod] = types
        return new_conf
    
    def copy_mod(self, mod_path: str, target: str) -> bool:
        if os.path.exists(target):
            mod_name = os.path.basename(target)
            self.msg("error", f"[!!] WARNING: Module: '{mod_name}' already exists in the library.", sender=self.name)
            return False
        try:
            shutil.copy2(mod_path, target)
            self.mod_count += 1
            return True
        except Exception as e:
            self.msg("error", f"[!!] ERROR Copying file: {e} [!!]", sender=self.name)
            return False
    
    def copying(self, mod_path: str, mod_types: str) -> None:
        dpath = self.items_path.get(mod_types)
        if not dpath:
            self.msg("error", f"[!!] ERROR: Unknown mod types: {types} [!!]", sender=self.name)
            return
        fname = os.path.basename(mod_path)
        dpath = os.path.join(dpath, fname)
        self.copy_mod(mod_path, dpath)


    def show_dlc(self) -> None:
        text = "\n----------- DLC List -------------\n"
        for dlc in os.listdir(self.dir_in):
            file = os.path.splitext(dlc)
            if file[0].startswith(self.dlc_name):
                text += f"-- {dlc}\n"
        self.msg("msg", text)
    
    def install_dlc(self, file_name: str) -> list:
        if not self.unpack(file_name):
            self.msg("error", f"[!!] ERROR: Installing DLC: {file_name} [!!]", sender=self.name)
            return []
        items = []
        for root, dirs, files in os.walk(self.dir_temp):
            for name in files:
                items.append(os.path.join(root, name))
        return items
    
    def install(self, file_name: str) -> None:
        self.mod_count = 0
        mods = []
        if file_name == "*":
            for dlc in os.listdir(self.dir_in):
                if dlc.startswith(self.dlc_name):
                    mods.extend(self.install_dlc(dlc))
        else:
            mods.extend(self.install_dlc(file_name))
        conf = self.read_config(mods)
        conf = self.correct_config(conf, mods)
        for path, types in conf.items():
            self.copying(path, types)
        self.msg("msg", f"DLC installed successfully. {self.mod_count} new modules added.", sender=self.name)






