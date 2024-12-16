import textwrap

class Texter:
    def __init__(self, len_first_column: int = 25, len_second_column: int = 80, len_third_column: int = None, add_end_line: bool = False):
        self.len_first = len_first_column
        self.len_second = len_second_column
        self.len_thrid = len_third_column
        if not len_third_column:
            self.len_thrid = 60
        self.end_line = add_end_line
    

    def make_2column(self, text1: str, text2: str, width1: int = None, width2: int = None) -> str:
        if not width1:
            width1 = self.len_first
        if not width2:
            width2 = self.len_second
        new_text2 = textwrap.fill(text2, width=width2, subsequent_indent=" " * width1)
        if self.end_line:
            return f"{text1:<{width1}}{new_text2}\n"
        return f"{text1:<{width1}}{new_text2}"


    def make_3column(self, text1: str, text2: str, text3: str, width1: int = None, width2: int = None, width3: int = None) -> str:
        if not width1:
            width1 = self.len_first
        if not width2:
            width2 = self.len_second
        if not width3:
            width3 = self.len_thrid
        new_text3 = textwrap.fill(text3, width=width3, subsequent_indent=" " * (width1 + width2))
        if self.end_line:
            return f"{text1:<{width1}}{text2:<{width2}}{new_text3}\n"
        return f"{text1:<{width1}}{text2:<{width2}}{new_text3}"

class Texter4C:
    def __init__(self, len_first: int = 25, len_second: int = 25, len_third: int = 25, len_fourth: int = 60, add_new_line: bool = False):
        self.len_1 = len_first
        self.len_2 = len_second
        self.len_3 = len_third
        self.len_4 = len_fourth
        self.new_line = add_new_line

    def make_4column(self, text1: str, text2: str, text3: str, text4: str, width1: int = None, width2: int = None, width3: int = None, width4: int = None) -> str:
        if not width1:
            width1 = self.len_1
        if not width2:
            width2 = self.len_2
        if not width3:
            width3 = self.len_3
        if not width4:
            width4 = self.len_4
        text4 = textwrap.fill(text4, width=width4, subsequent_indent=" " * (width1 + width2 + width3))
        text = f"{text1:<{width1}}{text2:<{width2}}{text3:<{width3}}{text4}"
        if self.new_line:
            text += "\n"
        return text



    

