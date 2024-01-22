import json
import os
import re

from typing import Union


class PostMan:
    def __init__(self, draco_callback: object):
        self.draco = draco_callback
        self.extrasDIR = self.draco.extrasDir
    
    def loadServer(self, name: str) -> Union[dict, bool]:
        fpath = os.path.join(self.extrasDIR, f"{name}.server")
        if not os.path.exists(fpath):
            self.draco.Msg(f"[!!] ERROR: File: {fpath} does not exists [!!]")
            return None
        with open(fpath, "r") as f:
            data = f.read()
        try:
            data = json.loads(data)
            self.draco.Msg(f"Load data successfull")
            return data
        except json.JSONDecodeError as e:
            self.draco.Msg(f"[!!] ERROR: convert data to json: {e} [!!]")
            return None
    
    
    def saveServer(self, name: str, config: dict) -> None:
        fpath = os.path.join(self.extrasDIR, f"{name}.server")
        try:
            data = json.dumps(config, indent=2)
        except json.JSONDecodeError as e:
            self.draco.Msg(f"[!!] ERROR: decode config to json: {e} [!!]")
            return
        try:
            with open(fpath, "w") as f:
                f.write(data)
            self.draco.Msg(f"Save <{name}> Config Successfull")
        except Exception as e:
            self.draco.Msg(f"[!!] ERROR: Save Config file: {e} [!!]")
    
    def listServers(self) -> None:
        msg = "\n********** Server List: ************\n"
        for serv in os.listdir(self.extrasDIR):
            tag = serv.find(".")
            if tag == -1:
                continue
            if serv[tag:] == ".server":
                msg += "--  " + serv[0:tag] + "\n"
        self.draco.Msg(msg)
