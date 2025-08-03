
from .generator_tools.bytes_hide import BytesHide


class MasterGenTools:
    def __init__(self, wrapper: object):
        self.wrapper = wrapper
        self.msg = self.wrapper.msg
        self.BytesHide = BytesHide(self)
    

    def scode_single_char(self, raw_scode: str, char: str = "#", last_char: str = "0", separator: str = ",", new_line: bool = True) -> str:
        # convert shellcode to string with multiple single char
        # ex: 0x04 -> "####"
        # ex: 0x07 -> "#######"
        return self.BytesHide.single_char_generator(raw_scode, char, last_char, separator, new_line)
        
