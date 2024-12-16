import os
import sys
from typing import Union

#FLAGS:
# 1 - Linux 32 bit elf binary


class AsmCompiler:
    def __init__(self, file_name: str, flag: Union[int, str] = 1):
        self.name = "ASM Compiler"
        self.flag = str(flag)
        self.fname = file_name
        self._fname, self.fext = os.path.splitext(file_name)
        self.dir_items = "/items"
        self.dir_hive = "/hive"
        self.dir_lab = "/lab"


    
    def get_source_file(self) -> Union[str, None]:
        src = os.path.join(self.dir_hive, self.fname)
        for f in os.listdir(src):
            if self.fname in src:
                src_file = os.path.join(src, f)
                print(f"[{self.name}] Find source file")
                return src_file
        print(f"[{self.name}] [!!] ERROR: Cannot find source file [!!]")
        return None
    
    def prepare_file(self) -> bool:
        src = self.get_source_file()
        if not src:
            return False
        os.system(f"cp {src} {self.dir_lab}/{self.fname}")
        return True
    
    def compile(self) -> None:
        if not self.prepare_file():
            return
        match self.flag:
            case "1":
                self.linux32bit()
            case _:
                print(f"[{self.name}] [!!] ERROR: Unknown Compile Option. [!!]")
                return
        self.last_job()
        print("DONE")
    
    def linux32bit(self) -> None:
        print(f"[{self.name}] Start Compiling 'elf32'")
        os.system(f"cd {self.dir_lab} && nasm -f elf32 -o {self._fname}.o {self.fname}")
        os.system(f"cd {self.dir_lab} && ld -m elf_i386 -o {self._fname} {self._fname}.o")
        print(f"[{self.name}] Compile Done")
    
    def last_job(self) -> None:
        os.system(f"cp {self.dir_lab}/{self._fname} {self.dir_hive}/{self.fname}/{self._fname}")
        os.system(f"cd {self.dir_lab} && rm {self.fname} && rm {self._fname}.o && rm {self._fname}")
        os.system(f"chmod 777 {self.dir_hive}/{self.fname}/{self._fname}")
        print(f"[{self.name}] Clean temp files complete. Worm is ready.")


if __name__ == "__main__":
    argv = sys.argv
    if len(argv) > 2:
        comp = AsmCompiler(argv[1], argv[2])
        comp.compile()
    elif len(argv) > 1:
        comp = AsmCompiler(argv[1])
        comp.compile()
    else:
        print("Cant run compiler")

        