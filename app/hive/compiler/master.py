from typing import Union, Callable
from .core.linux_comp import LinuxPythonCompilerCore
from .core.multi_comp import MultiCompCore
# from .core.cython_cross import CrossCythonCore
from .core.py_wine import WinePY



class CompilerObject:
    def __init__(self, name: str, info: str, target_system: str, master_compiler: object, compiler: object):
        self.name = name
        self.info = info
        self.master = master_compiler
        self.compiler = compiler
        self.target_sys = target_system



        
class MasterCompiler:
    def __init__(self, queen: object):
        self.name = "MasterCompiler"
        self.queen = queen
        self.msg = self.queen.msg
    
    def mount_core(self) -> None:
        self.wine_py = WinePY(self)
        self.linux_py = LinuxPythonCompilerCore(self)
        self.multi = MultiCompCore(self)
        # self.cross_c = CrossCythonCore(self)
        self.main_comp = {
            "WinePy": self.wine_py,
            "LinuxPy" : self.linux_py,
            "MultiComp" : self.multi,
            # "CrossCy" : self.cross_c
        }
        self.compilers = self.compiler_list()
    
    def compiler_list(self) -> dict:
        comp = {
            "WinePyInst" : CompilerObject("WinePyInst", "Compiler using PyInstaller along with python 3.12. Uses wine emulator and Pyinstaller module to build EXE.", "windows", self, self.wine_py),
            "WinePyNuitka" : CompilerObject("WinePyNuitka", "A compiler using Nuitka and Python 3.12. Builds an executable file using the Wine emulator and Nuitka module.", "windows", self, self.wine_py),
            "MC_elf32" : CompilerObject("MC_elf32", "Assembler Compiler. Builds the executable file elf32 32bit", "linux", self, self.multi),
            "MC_win32" : CompilerObject("MC_win32", "Assembler Compiler. Builds a win32 32bit exe executable file", "windows", self, self.multi),
            "LinPyIn"   : CompilerObject("LinPyIn", "Python3.11 compiler and 'Pyinstaller' on linux. Builds Linux executables using python 3.11 and the 'PyInstaller' module.", "linux", self, self.linux_py),
            # "CyApp" : CompilerObject("CyApp", "Kros compiler 'cython' with python 3.12. Builds small exe file with additional libraries. Does not build single file exe.", "windows", self, self.cross_c)
        }
        return comp


    def check_core(self) -> None:
        if not self.wine_py.status:
            self.msg("error", f"[!!] WARNING: No 'WinePy' compiler installed. You won't be able to build windows EXEs [!!]")
        else:
            self.msg("msg", f"Compiler Core: '{self.wine_py.name}' is ready. You can build EXE file.")
        if not self.linux_py.status:
            self.msg("error", f"[!!] WARNING: No 'LinuxPy' compiler installed. You won't be able to build linux exe [!!]")
        else:
            self.msg("msg", f"Compiler Core: '{self.linux_py.name}' is ready. You can build linux executable files.")
        if not self.multi.status:
            self.msg("error", f"[!!] WARNING: No 'MultiComp' compiler installed. You won't be able to build other win/linux binary [!!]")
        else:
            self.msg("msg", f"Compiler Core: '{self.multi.name}' is ready. You can build extra win/linux binary")
        # if not self.cross_c.status:
        #     self.msg("error", f"[!!] WARNING: No 'CrossCython' compiler installed. You won't be able to build Cython Windows EXE [!!]")
        # else:
        #     self.msg("msg", f"Compiler Core: '{self.cross_c.name}' is ready. You can build Cython EXE binary")
    
    def work(self) -> None:
        self.mount_core()
        self.check_core()
    
    def install(self, name: str, with_mods: bool = True) -> None:
        if name == "all":
            for comp in self.main_comp.values():
                comp.install()
                if with_mods:
                    comp.install_modules()
        else:
            comp = self.main_comp.get(name)
            if not comp:
                self.msg("error", f"[!!] ERROR: Compiler: '{name}' does not exists [!!]", sender=self.name)
                return
            comp.install()
            if with_mods:
                comp.install_modules()
       
    
    def install_module(self, name: str) -> None:
        master = self.main_comp.get(name)
        if not master:
            self.msg("error", f"[!!] ERROR: Master Compiler: '{name}' does not exists [!!]", sender=self.name)
            return
        if not master.status:
            self.msg("error", f"[!!] ERROR: Compiler: '{name}' is not installed. Please install neccessary module. [!!]", sender=self.name)
            return
        master.install_modules()
    
    def install_modules(self) -> None:
        for comp in self.main_comp.values():
            comp.install_modules()

    def show_compilers(self) -> None:
        text = "--------- All Compilers: -----------\n"
        for comp in self.compilers.values():
            text += "-" * 100 + "\n"
            text += f"--- Master Compiler: {comp.compiler.name}\n"
            text += f"--- Name: {comp.name}\n"
            text += f"--- Target System: {comp.target_sys}\n"
            text += f"--- Description: {comp.info}\n"
            if comp.compiler.status:
                text += f"--- Compiler is ready ---\n"
            else:
                text += "--- Compiler NOT INSTALLED ---\n"
        self.msg("msg", text, sender=self.name)
    
    def compile(self, worm_pipeline: object) -> object:
        comp_name = worm_pipeline.gvar.get("COMPILER_NAME")
        if not comp_name:
            self.msg("error", "[!!] ERROR: Compiler name is not set [!!]", sender=self.name)
            worm_pipeline.last_error = 1
            return worm_pipeline
        comp = self.compilers.get(comp_name)
        if not comp:
            self.msg("error", f"[!!] ERROR: Compiler name: '{comp_name}' does not exists [!!]", sender=self.name)
            worm_pipeline.last_error = 1
            return worm_pipeline
        worm_pipeline = comp.compiler.compile_worm(worm_pipeline)
        worm_pipeline._to_dev.append(worm_pipeline.exe_file_path)
        return worm_pipeline
