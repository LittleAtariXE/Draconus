import os
from typing import Union


class Icons:
    def __init__(self, worm_builder: object, queen: object):
        self.wb = worm_builder
        self.dir_icons = self.wb.dir_icons
        self.queen = queen
        self.dir_out = self.queen.dir_hive_out
        self.icon = None
    
    @property
    def icon_list(self) -> list:
        icons = []
        for file in os.listdir(self.dir_icons):
            icons.append(file)
        return icons
    
    def set_icon(self, name: str) -> Union[None, str]:
        if name in self.icon_list:
            return os.path.join(self.dir_icons, name)
        else:
            return None
    



    