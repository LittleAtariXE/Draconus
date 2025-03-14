
from typing import Union
from random import choice, randint

class TT_MOD_Dustman:
    def __init__(self, template_tools: object):
        self.TT = template_tools
    
    def random_string(self, data_base: Union[list, tuple, set]) -> str:
        text = choice(data_base)
        return text
    
    def random_version(self, separator: str = ".", number_count: str = "random") -> str:
        first = randint(1, 3)
        if number_count == "random":
            num = randint(2,4)
        else:
            try:
                number_count = int(number_count)
                num = number_count
            except:
                num = randint(2,4)
        ver = f"{first}{separator}"
        while len(ver.split(separator)) < num + 1:
            ver += f"{randint(0,9)}{separator}"
        return ver.rstrip(separator)
    
    def generate_number(self, min_num: int, max_num: int) -> int:
        return randint(min_num, max_num + 1)

