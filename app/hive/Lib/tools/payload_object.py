from typing import Union


class PayloadObject:
    def __init__(self, lib_item_name: str, lib_item: object):
        self.lib_item = lib_item
        self.name = lib_item_name
        self.work_step = []
        self.options = {
            # use render to return code
            "render_FLAG" : True,
            "include_py_import" : True,
            "binary_file" : False,
        }
       
    def add_step(self, step_name: str) -> None:
        self.work_step.append(step_name)
    
    def set_option(self, option_name: str, value: any) -> None:
        self.options[option_name] = value

    def read_headers(self, headers: list) -> None:
        match headers[0]:
            case "step":
                self.add_step(headers[1])
            case "options":
                self.set_option(headers[1], headers[2])
    