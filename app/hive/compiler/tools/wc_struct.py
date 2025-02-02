

class DLL_Struct:
    def __init__(self, worm_pipe: object):
        self.wp = worm_pipe
        self.src_temp_dll = None
        self.code = None
        self.file_name = "steam.dll"
        self.export_func = []
        self.lib_name = None
        self.def_file_path = None
        self.file_path = None
        self.raw_file_name = None
        self.raw_file_path = None
        
    def update(self, var: dict, key: str) -> None:
        lkey = len(key)

        for k, i in var.items():
            if k[0:lkey] == key:

                if k[lkey:] == "export_func":
                    if isinstance(k, list):
                        self.export_func.extend(i)
                    else:
                        self.export_func.append(i)
                    continue
                self.__setattr__(k[lkey:], i)
                
        

