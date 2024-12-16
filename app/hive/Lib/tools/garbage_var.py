
from typing import Union

class GarbageVar:
    def __init__(self, name: str, default_value: Union[str, int] = 16, sheme_types: str = "eye", info: str = "", owner: str = None):
        self.name = name
        self.default = default_value
        self.sheme = sheme_types
        self.info = info
        self.owner = owner
        self._value = None
    
    @property
    def value(self) -> any:
        if not self._value:
            return self.default
        else:
            return self._value
    
    def set_value(self, value: Union[str, int]) -> bool:
        self._value = value
        return True
        
    
    
