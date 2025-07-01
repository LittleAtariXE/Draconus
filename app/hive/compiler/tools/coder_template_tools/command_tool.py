

class CommandTool:
    def __init__(self, temp_tools: object):
        self.TT = temp_tools
    

    def script_loader(self, script: str, loader: str, loader_char: str = "$") -> str:
        return loader.replace(loader_char, script)


