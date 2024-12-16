import string
from random import randint
from typing import Union

class GarbageMan:
    def __init__(self, coder: object):
        self.coder = coder
        self.first_chain = string.ascii_letters
        self.chars = string.ascii_letters + string.digits
        self.max_len = len(self.chars)
        self.eye_char_table = [("m", "n"), ("n", "m"), ("o", "O"), ("O", "o")]
        self.temp = set()
    
    def clear_memory(self) -> None:
        self.temp = set()
    
    def generate_trash(self, count: int = 16) -> str:
        count = int(count)
        trash = self.first_chain[randint(0, len(self.first_chain) - 1)]
        while len(trash) < count:
            char = self.chars[randint(0, self.max_len - 1)]
            trash += char
        return trash


    def eye_var(self, count: int, chars: tuple = None) -> str:
        count = int(count)
        if not chars:
            chars = self.eye_char_table[randint(0, len(self.eye_char_table) - 1)]
        many, one = chars
        for _ in range(100):
            postion_one = randint(1, count -1)
            var_name = many
            while len(var_name) < count:
                if len(var_name) == postion_one:
                    var_name += one
                var_name += many
            if var_name in self.temp:
                continue
            else:
                self.temp.add(var_name)
                return var_name
        return None


    def generate(self, garVar: object) -> Union[str, None]:
        match garVar.sheme:
            case "eye":
                return self.eye_var(garVar.value)
            case "randC":
                return self.generate_trash(garVar.value)
            case _:
                return None
        return None

