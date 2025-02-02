import os

from .queen_mods.local_messanger import LocalMessanger

from .Lib.library import Library
from .Lib.dlc import DLC
from .Lib.tools.shortcuts import Shortcuts
from .worm_builder.worm_config import WormBuilder
from .compiler.coder import Coder
from .compiler.master import MasterCompiler
from .compiler.worm_constructor import WormConstructor

class Queen:
    def __init__(self, builder_object: object):
        self.conf = builder_object
        self.conf.make_dirs()
        self.dir_hive = os.path.dirname(__file__)
        self.dir_hive_out = self.conf.dir_hive_out
        self.dir_etc = os.path.join(self.dir_hive, "etc")
        self.dir_lib = os.path.join(os.path.dirname(__file__), "Lib")
        self.msg = LocalMessanger(self)
        self.global_opt = {}
        



    def load_modules(self) -> None:
        self.Lib = Library(self)
        self.worm = WormBuilder(self)
        self.master = MasterCompiler(self)
        self.master.work()
        self.coder = Coder(self, self.worm)
        self.worm_constructor = WormConstructor(self.coder, self.master)
        self.short = Shortcuts(self)
        self.short.make_shortcuts()
        self.dlc = DLC(self.Lib)
        self.msg("msg", "Hive is ready. Check Compilers ....")

    
    def enter(self) -> None:
        self.load_modules()
    
    def install(self) -> None:
        self.master.install()
    
    def install_modules(self) -> None:
        self.master.install_modules()
    
    def install_DLC(self, dlc_name: str) -> None:
        self.dlc.install(dlc_name)
        self.Lib.find_items()
    
    def clear_worm(self) -> None:
        self.worm = WormBuilder(self)
        self.coder = Coder(self, self.worm)
        self.worm_constructor = WormConstructor(self.coder, self.master)
        self.msg("msg", "Start new worm template")
    
    def show_worm(self) -> None:
        self.worm.show_all()
    
    def show_compilers(self) -> None:
        self.master.show_compilers()
    
    def show_items(self, types: str) -> None:
        self.Lib.show_items(types)
    
    def show_process_list(self) -> None:
        self.Lib.show_process_worm()
    
    def show_dlc(self) -> None:
        self.dlc.show_dlc()
    
    def add_worm_item(self, types: str, name: str, target: str = None) -> None:
        self.worm.Add(types, name, target)
    
    def add_variable(self, name: str, value: any, types: str = None) -> None:
        self.worm.add_variable(name, value, types)
    
    def add_food(self, src_food_name: str, target_var_name: str) -> None:
        self.worm.add_food_as_var(src_food_name, target_var_name)
    
    def add_global_var(self, name: str, value: str) -> None:
        self.worm.add_globalVar(name, value)
    
    def show_global_var(self) -> None:
        self.worm.show_global_var(True)   

    def build_worm(self, options: dict = {}):
        self.worm_constructor.build_WORM(options)

    def Run(self) -> None:
        pass
        
        
        
        
        

    
    