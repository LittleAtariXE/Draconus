import os

class IncludeCode:
    def __init__(self, source_name: str, in_code_name: str, support_file_dir_path: str):
        self.source_name = source_name
        self.in_code_name = in_code_name
        self.include_dir = support_file_dir_path
        self.fpath = os.path.join(self.include_dir, self.source_name)
        self.options = {}

    
    @property
    def raw_code(self) -> str:
        return self._load_code()
    
    def _load_code(self) -> str:
        try:
            with open(self.fpath, "r") as file:
                data = file.read()
        except:
            data = ""
        return data
    
    def add_options(self, data: str) -> None:
        data = data.split(":")
        self.options[data[0]] = data[1]


    
