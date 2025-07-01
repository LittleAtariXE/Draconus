from .lib_item import LibItem

class ShellCodeItem(LibItem):
    def __init__(self, fpath: str):
        super().__init__(fpath)
        
        ## shellcode contain null bytes
        self.NullBytes = False

        self.make_in()
    

    def make_in(self):
        fdata = self.load_item_data()
        for d in fdata:
            d = d.split(self._separator)
            match d[0]:
                case "NullBytes":
                    if d[1] == "False":
                        self.NullBytes = False
                    else:
                        self.NullBytes = True
                    