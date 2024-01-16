import string
from random import randint


class MrHeader:
    def __init__(self, length=30):
        self.length = length
        self.base_char = string.ascii_letters + string.digits + string.punctuation
        self.ban_char = ["'", '"', "\\"]
    
    def generate_name(self):
        header = ""
        while len(header) < self.length:
            char = self.base_char[randint(0, len(self.base_char) - 1)]
            if char in self.ban_char:
                continue
            header += char
        return header

