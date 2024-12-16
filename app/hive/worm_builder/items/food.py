
from typing import Union

class Food:
    def __init__(self, library: object):
        self.lib = library
        self.food_items = self.lib.lib["food"]
    
    def eat(self, food_var: object) -> Union[object, None]:
        food_item = self.food_items.get(food_var.name)
        if not food_item:
            return None
        food_var.set_value(food_item.value)
        return food_var
    
    
    
