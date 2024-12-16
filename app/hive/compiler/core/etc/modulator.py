import sysconfig
import sys
import modulefinder
import pkgutil
import os

class Modulator:
    def __init__(self):
        self.important_mods = {'builtins', 'sys', 'os', 're', 'contextlib', 'collections', 'importlib', 'encodings', 'codecs'}
    
    @property
    def standard_modules(self) -> set:
        mods = set()
        # check modules in stdlib directory
        stdlib_path = sysconfig.get_paths()["stdlib"]
        for module in pkgutil.iter_modules([stdlib_path]):
            mods.add(module.name)
        
        # Embedded modules not included in the list of standard modules
        emods = sys.builtin_module_names
        mods.update(emods)
        return mods
    
    def find_modules(self, file_path: str) -> set:
        finder = modulefinder.ModuleFinder()
        finder.run_script(file_path)
        return set(finder.modules.keys())
    
    def generate_excludes_mods(self, file_path: str) -> list:
        smods = self.standard_modules
        wmods = self.find_modules(file_path)
        excludes = smods - wmods
        excludes = excludes - self.important_mods
        print(list(excludes))
        return list(excludes)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        mod = Modulator()
        mod.generate_excludes_mods(sys.argv[1])



