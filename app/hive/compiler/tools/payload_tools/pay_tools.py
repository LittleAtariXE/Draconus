
from typing import Union

class PayloadTools:
    def __init__(self, payload_builder: object):
        self.pb = payload_builder
        self.msg = self.pb.msg
        self.format = self.pb.default_encode
    

    def add_executor(self, code: Union[str, bytes], command: str) -> str:
        if not isinstance(code, str):
            try:
                code = code.decode(self.format)
            except:
                code = str(code)
        cmd = command.split("$")
        if len(cmd) == 1:
            code = f"{cmd[0]}{code}"
        else:
            code = f"{cmd[0]}{code}{cmd[1]}"
        return code
    
    def format_powershell(self, code: Union[str, bytes]) -> str:
        if not isinstance(code, str):
            try:
                code = code.decode(self.format)
            except:
                self.msg("error", f"ERROR decode powershell script: {e}")
                code = str(code)
        code = code.split("\n")
        script = ""
        for line in code:
            if line.strip() == "\n" or line.strip() == "":
                continue
            script += f"{line}; "
        return script
    