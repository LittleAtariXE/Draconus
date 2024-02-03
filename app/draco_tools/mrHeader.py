import string
import os
from random import randint


class MrHeader:
    def __init__(self, extras_dir_path: str, length=30):
        self.length = length
        self.head_file = os.path.join(extras_dir_path, "headers.txt")
        self.base_char = string.ascii_letters + string.digits + string.punctuation
        self.ban_char = ["'", '"', "\\", "%"]
    
    def generate_name(self):
        header = ""
        while len(header) < self.length:
            char = self.base_char[randint(0, len(self.base_char) - 1)]
            if char in self.ban_char:
                continue
            header += char
        return header

    def loadHeader(self) -> str:
        if not os.path.exists(self.head_file):
            head = self.generate_name()
            with open(self.head_file, "w") as f:
                f.write(head)
        else:
            with open(self.head_file, "r") as f:
                head = f.read()
        return head
    
    