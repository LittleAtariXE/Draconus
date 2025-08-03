import docker
import os
from time import sleep
from typing import Union

from app.hive.etc.py_lib import PY_LIBRARY

class CrossComp:
    def __init__(self, master: object):
        self.master = master
        self.msg = self.master.queen.msg
        self.name = "CrossComp"
        self.dir_hive = self.master.queen.dir_hive_out
        self.dir_work = "/hive"
        self.dir_lab = "/lab"
        self.dir_etc = os.path.join(os.path.dirname(__file__), "etc")

        self.master_system_compiler = "littleatarixe/wine_py:1.0"
        self.compiler_container_name = "crosscomp"
        self.docker = docker.from_env()
        self._container_id = None

        # library for linker
        self._DLL = "-lkernel32 -lmsvcrt -luser32 -lshell32 -lws2_32 -lshlwapi"

        self.info = "Allows cross compilation to exe windows. Compiles python using PyInstaller or Nuitika. Compiles Assembler, C, C++ code to exe, dll. Main compiler."

    @property
    def status(self) -> bool:
        return self.get_compiler()
    
    @property
    def compiler(self) -> Union[object, None]:
        return self.get_compiler(True)
    
    def check_master_system(self) -> bool:
        try:
            container = self.docker.images.get(self.master_system_compiler)
            return True
        except docker.errors.ImageNotFound:
            return False
    
    def create_container(self) -> object:
        comp = self.docker.containers.create(
            image=self.master_system_compiler,
            command="sleep infinity",
            name=self.compiler_container_name,
            volumes={
                self.dir_hive : {"bind" : self.dir_work, "mode" : "rw"},
                self.dir_etc : {"bind" : self.dir_lab, "moder" : "rw"}
            },
            detach=True
        )
        return comp
    
    def pull_image(self, image_name: str) -> None:
        pull_output = self.docker.api.pull(image_name, stream=True, decode=True)
        for line in pull_output:
            if 'status' in line:
                self.msg("msg", f"Status: {line['status']}", sender=self.name)
            if 'progress' in line:
                self.msg("msg", f"Progress: {line['progress']}", sender=self.name)
            if 'id' in line:
                self.msg("msg", f"ID: {line['id']} - {line['status']} {line.get('progress', '')}", sender=self.name)
        self.msg("msg", "Downloading Complete")
    
    def get_compiler(self, check: bool = False) -> Union[None, object]:
        if not self.check_master_system():
            self.msg("error", f"[!!] ERROR '{self.name}': No master system compiler image downloaded. Install the necessary modules. [!!]")
            return None
        if self._container_id:
            return self.docker.containers.get(self._container_id)
        
        for con in self.docker.containers.list(all=True):
            if con.name == self.compiler_container_name:
                self._container_id = con.id
                comp = self.docker.containers.get(self._container_id)
                return comp

        if not check:
            return None
        return self.create_container()
    
    def exec_cmd(self, command: str) -> object:
        exec_id = self.docker.api.exec_create(self.compiler.id, f"bash -c '{command}'")
        output = self.docker.api.exec_start(exec_id, stream=True)
        for line in output:
            self.msg("msg", line.decode().strip(), sender=self.name)
    
    def install(self) -> None:
        if self.status:
            self.msg("msg", f"Core: '{self.name}' is installed")
            return
        self.msg("msg", "Start image downloads. This may take some time.", sender=self.name)
        sleep(1)
        self.pull_image(self.master_system_compiler)
        self.msg("msg", "Get image...", sender=self.name)
        comp = self.compiler
        if not comp:
            self.msg("error", f"[!!] ERROR '{self.name}': building compiler [!!]", sender=self.name)
            return
        self.build_lab()
    
    def build_lab(self) -> None:
        self.msg("msg", "[!!] Start of laboratory construction .... [!!]", sender=self.name)
        self.compiler.start()
        sleep(1)
        # self.update_repo()
        
        self.exec_cmd("apt update")
        self.exec_cmd("apt install nasm binutils -y")
        self.exec_cmd("apt install python3 -y")
        self.exec_cmd("apt install -y gcc-mingw-w64-i686")
        # self.exec_cmd("apt install -y upx-ucl")
        self.exec_cmd("apt install -y mingw-w64")
        self.msg("msg", "------ Install Modules ------", sender=self.name)
        self.msg("msg", ", ".join(PY_LIBRARY), sender=self.name)
        for mod in PY_LIBRARY:
            self.exec_cmd(f"wine python -m pip install {mod}")
        self.msg("msg", "Building laboratory complete. Stoping container ....")
        self.compiler.stop()
        self.msg("msg", f"[{self.name}] is ready.")
    
    def install_modules(self) -> None:
        if not self.compiler:
            self.msg("error", "[!!] ERROR: Compiler is not installed [!!]", sender=self.name)
            return
        self.msg("msg", f"Start Compiler: {self.name}")
        self.compiler.start()
        sleep(0.5)
        self.msg("msg", "------ Install Modules ------", sender=self.name)
        self.msg("msg", ", ".join(PY_LIBRARY), sender=self.name)
        for mod in PY_LIBRARY:
            self.exec_cmd(f"wine python -m pip install {mod}")
        self.msg("msg", "DONE", sender=self.name)
        self.msg("msg", "Stopping Compiler ......")
        self.compiler.stop()
    
    def build_rc_file_command(self, raw: object) -> object:
        raw.cs_cmd = None
        raw.cs_res_name = None
        match raw.compiler:
            case "mingw-x32":
                cmd = "i686-w64-mingw32-windres"
            case "mingw-x64":
                cmd = "x86_64-w64-mingw32-windres"
            case _:
                cmd = None
        if not cmd:
            self.msg("error", f"[!!] ERROR: Builiding res file. No match compiler: '{raw.compiler}' [!!]")
            return raw
        rc_name = os.path.splitext(raw.cs_file_name)[0]
        cmd += f" {raw.cs_file_name} -O coff -o {rc_name}.res"
        raw.cs_cmd = cmd
        raw.cs_res_name = rc_name
        return raw
    
    def compile_DLL(self, raw: object) -> object:
        match raw.compiler:
            case "mingw-x32":
                cmd_comp = "i686-w64-mingw32-gcc"
            case _:
                self.msg("error", f"[!!] ERROR: Compiler: '{raw.compiler}' is not supported [!!]", sender=self.name)
                raw.last_error = 1
                return raw
        if raw.cs:
            self.msg("dev", "Builiding res command", sender=self.name)
            raw = self.build_rc_file_command(raw)
        self.msg("msg", f"Builiding DLL file: '{raw.lib.name}'", sender=self.name)
        self.msg("msg", f"Start Compiler: {raw.compiler}", sender=self.name)
        self.compiler.start()
        if raw.cs_cmd:
            self.msg("msg", f"Builiding res file", sender=self.name)
            self.exec_cmd(f"cd {self.dir_work} && cd {raw.name} && {raw.cs_cmd}")
        raw_lib = raw.lib.name.rstrip(".dll")
        cmd = f"nasm -f win32 {raw.raw_code_file_name} -o {raw_lib}.o"
        self.exec_cmd(f"cd {self.dir_work} && cd {raw.name} && {cmd}")
        cmd = f"{cmd_comp} -shared {raw_lib}.o {raw.lib.def_fname}"
        if raw.cs_res_name:
            cmd += f" {raw.cs_res_name}.res"
        cmd += f" -o {raw.lib.name}"
        if raw.gvar.get("NO_DLL"):
            cmd += " -nostdlib -s"
        cmd += f" {self._DLL} -Wl,--entry=DllMain"
        self.msg("dev", cmd, sender=self.name)
        self.exec_cmd(f"cd {self.dir_work} && cd {raw.name} && {cmd}")
        self.exec_cmd(f"cd {self.dir_work} && cd {raw.name} && chmod 777 *")
        self.msg("msg", "Stoping Compiler: mingw-x32", sender=self.name)
        self.compiler.stop()
        raw.ready_app.append(os.path.join(raw.work_dir, raw.lib.name))
        return raw
    
    def _create_res_cmd(self, compiler_name: str, rc_file_name: str, output_file_name: str = None) -> Union[str, None]:
        match compiler_name:
            case "mingw-x32":
                cmd = "i686-w64-mingw32-windres"
            case "mingw-x64":
                cmd = "x86_64-w64-mingw32-windres"
            case _:
                self.msg("error", f"[!!] ERROR: Compiler: '{compiler_name}' is not supported [!!]", sender=self.name)
                return None
        if not output_file_name:
            output_file_name = os.path.splitext(compiler_name)[0]
        cmd += f" {rc_file_name} -O coff -o {output_file_name}.res"
        return cmd


    def compile_DLL2(self, dll: object) -> object:
        match dll.compiler:
            case "mingw-x32":
                cmd_comp = "i686-w64-mingw32-gcc"
                cmd_raw = "nasm -f win32"
            case "mingw-x64":
                cmd_comp = "x86_64-w64-mingw32-gcc"
                cmd_raw = "nasm -f win64"
            case _:
                self.msg("error", f"[!!] ERROR: Compiler: '{dll.compiler}' is not supported [!!]", sender=self.name)
                dll.last_error = 1
                return dll
        rc_cmd = None
        if dll.cs:
            self.msg("dev", "Builiding res command", sender=self.name)
            rc_cmd = self._create_res_cmd(dll.compiler, dll.cs_fname, dll.raw_name)
        self.msg("msg", f"Builiding DLL file: '{dll.name}'", sender=self.name)
        self.msg("msg", f"Start Compiler: {dll.compiler}", sender=self.name)
        self.compiler.start()
        if rc_cmd:
            self.msg("msg", f"Builiding res file", sender=self.name)
            self.msg("dev", rc_cmd, sender=self.name)
            self.exec_cmd(f"cd {self.dir_work} && cd {dll.work_dir_name} && {rc_cmd}")
        raw_name = dll.name.rstrip(".dll")
        cmd_raw += f" {raw_name} -o {raw_name}.o"
        self.msg("dev", cmd_raw, sender=self.name)
        self.exec_cmd(f"cd {self.dir_work} && cd {dll.work_dir_name} && {cmd_raw}")
        cmd_comp += f" -shared {raw_name}.o {dll.def_fname}"
        if rc_cmd:
            cmd_comp += f" {raw_name}.res"
        cmd_comp += f" -o {dll.name}"
        if dll.no_dll:
            cmd_comp += f" -nostdlib -s"
        # check for library
        if len(dll.need_lib) > 0:
            nlib = " ".join(dll.need_lib)
            cmd_comp += f" {nlib}"
        # add standard library
        cmd_comp += f" {self._DLL} -Wl,--entry=DllMain"
        self.msg("msg", f"Building DLL file: '{dll.name}'")
        self.msg("dev", cmd_comp, sender=self.name)
        self.exec_cmd(f"cd {self.dir_work} && cd {dll.work_dir_name} && {cmd_comp}")
        self.exec_cmd(f"cd {self.dir_work} && cd {dll.work_dir_name} && chmod 777 *")
        self.msg("msg", f"Stoping Compiler: {dll.compiler}", sender=self.name)
        self.compiler.stop()
        
        return dll

        
    def mingw_x64_compile(self, raw: object) -> object:
        self.msg("msg", "Use mingw-x64", sender=self.name)
        if raw.cs:
            self.msg("dev", "Builiding res command", sender=self.name)
            raw = self.build_rc_file_command(raw)
        self.msg("msg", "Start Compiler: mingw-x64", sender=self.name)
        self.compiler.start()
        if raw.cs_cmd:
            self.msg("msg", f"Builiding res file", sender=self.name)
            self.exec_cmd(f"cd {self.dir_work} && cd {raw.name} && {raw.cs_cmd}")
        cmd = f"nasm -f win64 {raw.raw_code_file_name} -o {raw.name}.o"
        self.exec_cmd(f"cd {self.dir_work} && cd {raw.name} && {cmd}")
        cmd = "x86_64-w64-mingw32-gcc -m64"
        
        if raw.gvar.get("NO_DLL"):
            cmd += " -nostdlib -s"
        cmd += f" -o {raw.name}.exe {raw.name}.o"
        if raw.cs_res_name:
            cmd += f" {raw.cs_res_name}.res"
        # build entry point
        if raw.exe_show == "gui":
            cmd += f" -Wl,-e,WinMain"
        else:
            cmd += f" -Wl,-e,main"
        # add library
        if len(raw.libs) > 0:
            for lib in raw.libs:
                cmd += f" {lib.name}"
        # add dll
        if len(raw.need_lib) > 0:
            elib = ""
            for nl in raw.need_lib:
                elib += f" {os.path.join(self.dir_work, raw.name, nl)}"
            cmd += elib
        cmd += f" {self._DLL}"
        # console or gui program
        if raw.exe_show == "gui":
            cmd += " -mwindows"
        self.msg("msg", f"Building worm: '{raw.name}'", sender=self.name)
        self.msg("dev", cmd, sender=self.name)
        self.exec_cmd(f"cd {self.dir_work} && cd {raw.name} && {cmd}")
        self.exec_cmd(f"cd {self.dir_work} && cd {raw.name} && chmod 777 *")
        self.msg("msg", "Stoping Compiler: mingw-x64", sender=self.name)
        self.compiler.stop()
        raw.exe_file_name = f"{raw.name}.exe"
        raw.exe_file_path = os.path.join(raw.work_dir, raw.exe_file_name)
        raw.ready_app.append(raw.exe_file_path)
        return raw
    
    def mingw_x64_cpp_compile(self, raw: object) -> object:
        self.msg("msg", "Use mingw-x64-cpp", sender=self.name)
        if raw.cs:
            self.msg("dev", "Builiding res command", sender=self.name)
            raw = self.build_rc_file_command(raw)
        self.msg("msg", "Start Compiler: mingw-x64", sender=self.name)
        self.compiler.start()
        if raw.cs_cmd:
            self.msg("msg", f"Builiding res file", sender=self.name)
            self.exec_cmd(f"cd {self.dir_work} && cd {raw.name} && {raw.cs_cmd}")
        self.msg("msg", f"Building worm: '{raw.name}'", sender=self.name)
        cmd = f"x86_64-w64-mingw32-g++"
        cmd += f" -o {raw.name}.exe {raw.name}.cpp"
        # add support files
        if len(raw.sfiles) > 0:
            for sf in raw.sfiles:
                if sf.add_to_cmd:
                    cmd += f" {sf.file_name}"
        # add library
        if len(raw.libs) > 0:
            for lib in raw.libs:
                cmd += f" {lib.name}"
        # add dll
        if len(raw.need_lib) > 0:
            elib = ""
            for nl in raw.need_lib:
                elib += f" {os.path.join(self.dir_work, raw.name, nl)}"
            cmd += elib
        cmd += f" {self._DLL}"
        if raw.gvar.get("NO_DLL"):
            cmd += " -Os -s -Wl,--gc-sections"
        self.msg("dev", cmd, sender=self.name)
        self.exec_cmd(f"cd {self.dir_work} && cd {raw.name} && {cmd}")
        self.exec_cmd(f"cd {self.dir_work} && cd {raw.name} && chmod 777 *")
        self.msg("msg", "Stoping Compiler: mingw-x64", sender=self.name)
        self.compiler.stop()
        raw.exe_file_name = f"{raw.name}.exe"
        raw.exe_file_path = os.path.join(raw.work_dir, raw.exe_file_name)
        raw.ready_app.append(raw.exe_file_path)
        return raw
    
    def mingw_x32_compile(self, raw: object) -> object:
        self.msg("msg", "Use mingw-x32", sender=self.name)
        if raw.cs:
            self.msg("dev", "Builiding res command", sender=self.name)
            raw = self.build_rc_file_command(raw)
        self.msg("msg", "Start Compiler: mingw-x32", sender=self.name)
        self.compiler.start()
        if raw.cs_cmd:
            self.msg("msg", f"Builiding res file", sender=self.name)
            self.exec_cmd(f"cd {self.dir_work} && cd {raw.name} && {raw.cs_cmd}")
        cmd = f"nasm -f win32 {raw.raw_code_file_name} -o {raw.name}.o"
        self.exec_cmd(f"cd {self.dir_work} && cd {raw.name} && {cmd}")
        cmd = "i686-w64-mingw32-gcc"
        
        if raw.gvar.get("NO_DLL"):
            cmd += " -nostdlib -s"
        cmd += f" -o {raw.name}.exe {raw.name}.o"
        if raw.cs_res_name:
            cmd += f" {raw.cs_res_name}.res"
        # add dll
        if len(raw.need_lib) > 0:
            elib = ""
            for nl in raw.need_lib:
                elib += f" {os.path.join(self.dir_work, raw.name, nl)}"
            cmd += elib
        cmd += f" {self._DLL}"
        # console or gui program
        if raw.exe_show == "gui":
            cmd += " -mwindows"
        self.msg("msg", f"Building worm: '{raw.name}'", sender=self.name)
        self.msg("dev", cmd, sender=self.name)
        self.exec_cmd(f"cd {self.dir_work} && cd {raw.name} && {cmd}")
        self.exec_cmd(f"cd {self.dir_work} && cd {raw.name} && chmod 777 *")
        self.msg("msg", "Stoping Compiler: mingw-x32", sender=self.name)
        self.compiler.stop()
        raw.exe_file_name = f"{raw.name}.exe"
        raw.exe_file_path = os.path.join(raw.work_dir, raw.exe_file_name)
        raw.ready_app.append(raw.exe_file_path)
        return raw

                
            
        
    
    def ldx32_compile(self, raw: object) -> object:
        self.msg("msg", "Use LD-x32", sender=self.name)
        cmd = f"nasm -f elf32 {raw.raw_code_file_name} -o {raw.name}.o"
        self.msg("msg", "Start Compiler: LD-x32", sender=self.name)
        self.compiler.start()
        self.msg("msg", cmd, sender=self.name)
        self.exec_cmd(f"cd {self.dir_work} && cd {raw.name} && {cmd}")
        cmd_ld = f"ld -m elf_i386 -o {raw.name} {raw.name}.o"
        self.msg("msg", cmd_ld, sender=self.name)
        self.exec_cmd(f"cd {self.dir_work} && cd {raw.name} && {cmd_ld}")
        self.exec_cmd(f"cd {self.dir_work} && cd {raw.name} && chmod 777 *")
        self.msg("msg", "Stoping Compiler: LD-x32", sender=self.name)
        self.compiler.stop()
        raw.exe_file_name = raw.name
        raw.exe_file_path = os.path.join(raw.work_dir, raw.exe_file_name)
        raw.ready_app.append(raw.exe_file_path)
        return raw
    
    def pyinstaller_compile(self, raw: object) -> object:
        self.msg("msg", "Use PyInstaller", sender=self.name)
        cmd = "wine pyinstaller"
        if raw.out_one_file:
            cmd += " --onefile"
        match raw.gvar["PROGRAM_TYPE"]:
            case "console":
                cmd += " --console"
            case "window":
                cmd += " --windowed"
        if raw.icon:
            cmd += f" --icon={worm_pipeline.icon_name}"
        upx = raw.gvar.get("USE_UPX")
        cmd += f" --name={raw.name} {raw.raw_code_file_name}"
        self.msg("msg", f"CMD: {cmd}", sender=self.name)
        self.compiler.start()
        self.exec_cmd(f"cd {self.dir_work} && cd {raw.name} && {cmd}")
        self.msg("msg", "Compile Done", sender=self.name)
        self.exec_cmd(f"cp {self.dir_work}/{raw.name}/dist/{raw.name}.exe {self.dir_work}/{raw.name}/{raw.name}.exe")
        self.exec_cmd(f"chmod 777 {self.dir_work}/{raw.name}/{raw.name}.exe")
        self.exec_cmd(f"cd {self.dir_work} && cd {raw.name} && rm -R build/")
        self.exec_cmd(f"cd {self.dir_work} && cd {raw.name} && rm -R dist/")
        self.exec_cmd(f"chmod 777 {self.dir_work}/{raw.name}/{raw.name}.exe")
        self.msg("msg", "Stopping Compiler ......")
        self.compiler.stop()
        raw.exe_file_name = f"{raw.name}.exe"
        raw.exe_file_path = os.path.join(raw.work_dir, raw.exe_file_name)
        raw.ready_app.append(raw.exe_file_path)
        return raw
    
    def library_lib64_compile(self, raw: object) -> object:
        self.msg("msg", "Use mingw-x64", sender=self.name)
        self.msg("msg", "Start Compiler: mingw-x64", sender=self.name)
        self.compiler.start()
        for lib in raw.libs:
            self.msg("msg", f"Compile lib: {lib.raw_name}", sender=self.name)
            cmd = f"nasm -f win64 {lib.raw_name} -o {lib.raw_name}.o"
            self.exec_cmd(f"cd {self.dir_work} && cd {raw.name} && {cmd}")
            cmd = f"x86_64-w64-mingw32-ar rcs {lib.name} {lib.raw_name}.o"
            self.exec_cmd(f"cd {self.dir_work} && cd {raw.name} && {cmd}")
        self.msg("msg", "Stopping Compiler ......")
        self.compiler.stop()
        return raw
    
    def build_shellcode64(self, raw: object) -> object:
        self.msg("msg", "Use mingw-x64", sender=self.name)
        self.msg("msg", "Start Compiler: mingw-x64", sender=self.name)
        self.compiler.start()
        cmd = f"nasm -f bin {raw.raw_code_file_name} -o {raw.name}.o"
        self.msg("dev", cmd, sender=self.name)
        self.exec_cmd(f"cd {self.dir_work} && cd {raw.name} && {cmd}")
        cmd = f"objdump -D -b binary -mi386:x86-64 {raw.name}.o"
        # self.msg("msg", cmd, sender=self.name)
        self.exec_cmd(f"cd {self.dir_work} && cd {raw.name} && {cmd}")
        self.exec_cmd(f"cd {self.dir_work} && cd {raw.name} && {cmd} > {raw.name}_objdump.txt")
        self.exec_cmd(f"cd {self.dir_work} && cd {raw.name} && chmod 777 *")
        raw.bin_file_path = os.path.join(raw.work_dir, f"{raw.name}.o")
        self.msg("msg", "Stopping Compiler ......")
        self.compiler.stop()
        return raw