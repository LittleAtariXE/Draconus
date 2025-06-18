from typing import Union, Callable

from .core.cross_comp import CrossComp

class CompilerData:
    def __init__(self,
            name: str,
            info: str,
            master: object,
            compiler: object,
            target_os: str = "Windows",
            arch: str = "x64"):
        self.master = master
        self.comp = compiler
        self.name = name
        self.info = info
        self.target_os = target_os
        self.arch = arch
    
    @property
    def status(self) -> bool:
        return self.comp.status
    
    def status(self) -> str:
        if not self.comp.status:
            return "NOT INSTALLED"
        else:
            return "READY"


class MasterCompiler:
    def __init__(self, queen: object):
        self.queen = queen
        self.msg = self.queen.msg
        self.name = "MasterCompiler"
        self.compilers = {}
        self.cores = {}
        self.mount_core()
        self.check_core()
    
    def mount_core(self) -> None:
        # Cross Compiler
        self.cc = CrossComp(self)
        self.cores[self.cc.name] = self.cc
        self.compilers["PyInstaller"] = CompilerData("PyInstaller", "PyInstaller compiler with python 3.12 creates EXE for windows.", self, self.cc)
        self.compilers["mingw-x64"] = CompilerData("mingw-x64", "Mingw cross compiler, compiles EXE, DLL for windows x64.", self, self.cc)
        self.compilers["mingw-x32"] = CompilerData("mingw-x32", "Mingw cross compiler, compiles EXE, DLL for windows x86.", self, self.cc, arch="x86")
        self.compilers["LD-x32"] = CompilerData("LD-x32", "Compiles assembler files into executables on Linux x86 (32 bit).", self, self.cc, "Linux", "x86")

        

    
    def check_core(self) -> None:
        if not self.cc.status:
            self.msg("error", f"[!!] WARNING: '{self.cc.name}' is not installed. You will not be able to compile worms. Execute the command to install.")
        else:
            self.msg("msg", f"Master Compiler: {self.cc.name} is ready.")
    
    def show_compilers(self) -> None:
        text = "------------------------- COMPILERS: ----------------------------------\n"
        for comp in self.compilers.values():
            text += "-" * 80 + "\n"
            text += f"### IMAGE (Master Compiler) : {comp.comp.name}\n"
            text += f"### NAME : {comp.name}\n"
            text += f"### TARGET SYSTEM : {comp.target_os} {comp.arch}\n"
            text += f"### DESCRIPTION : {comp.info}\n"
            text += f"### STATUS : {comp.status()}\n"
        self.msg("msg", text)
    
    def install(self, compiler_name: str) -> None:
        comp = self.cores.get(compiler_name)
        if not comp:
            self.msg("error", f"ERROR: Compiler: '{compiler_name}' does not exists")
            return
        comp.install()

    def compile_dll(self, raw: object) -> object:
        return self.cc.compile_DLL(raw)
    
    def compile_library_lib(self, raw: object) -> object:
        return self.cc.library_lib64_compile(raw)
    
    def compile(self, raw: object) -> object:
        self.msg("msg", "Start Compiler")
        match raw.compiler:
            case "PyInstaller":
                raw = self.cc.pyinstaller_compile(raw)
            case "LD-x32":
                raw = self.cc.ldx32_compile(raw)
            case "mingw-x32":
                raw = self.cc.mingw_x32_compile(raw)
            case "mingw-x64":
                raw = self.cc.mingw_x64_compile(raw)
            case _:
                self.msg("error", f"[!!] ERROR: Compiler: '{raw.compiler}' does not exists [!!]")
        return raw
