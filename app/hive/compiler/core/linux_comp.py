import docker
import os
from time import sleep
from typing import Union

from app.hive.etc.py_linux_lib import PY_LINUX_LIBRARY


class LinuxPythonCompilerCore:
    def __init__(self, master: object):
        self.master = master
        self.msg = self.master.queen.msg
        self.name = "LinuxPy"
        self.dir_hive = self.master.queen.dir_hive_out
        self.dir_work = "/hive"

        self.master_system_compiler = "debian"
        self.compiler_container_name = "LinBuilder"
        self.docker = docker.from_env()
        self._container_id = None

        self._win = False
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
                self.dir_hive : {"bind" : self.dir_work, "mode" : "rw"}
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
            self.msg("msg", f"Core: '{self.name}' is installed", sender=self.name)
            return
        self.msg("msg", "Start image downloads. This may take some time.", sender=self.name)
        sleep(1)
        self.pull_image_with_progress(self.master_system_compiler)
        self.msg("msg", "Get image...")
        comp = self.compiler
        if not comp:
            self.msg("error", f"[!!] ERROR '{self.name}': building compiler [!!]", sender=self.name)
            return
        self.build_lab()
    
    def update_repo(self) -> None:
        self.exec_cmd('touch /etc/apt/sources.list')
        self.exec_cmd('echo "deb http://deb.debian.org/debian/ buster main" | tee -a /etc/apt/sources.list')
        self.exec_cmd('echo "deb-src http://deb.debian.org/debian/ buster main" | tee -a /etc/apt/sources.list')


    
    def build_lab(self) -> None:
        self.msg("msg", "[!!] Start of laboratory construction .... [!!]", sender=self.name)
        self.compiler.start()
        sleep(1)
        self.update_repo()
        self.exec_cmd("apt update")
        self.exec_cmd("apt install python3 python3-venv -y")
        self.exec_cmd("apt install python3-dev -y")
        self.exec_cmd("apt install libffi-dev libssl-dev build-essential upx-ucl -y")
        self.exec_cmd("mkdir /lab")
        self.exec_cmd("cd /lab && python3 -m venv ./venv")
        self.exec_cmd("cd /lab && ls -la")
        self.exec_cmd(f"cd /lab && source ./venv/bin/activate && pip install {' '.join(PY_LINUX_LIBRARY)}")
        self.exec_cmd(f"ls -la {self.dir_work}")
        self.msg("msg", "Building laboratory complete. Stoping container ....")
        self.compiler.stop()
        self.msg("msg", f"[{self.name}] is ready.")
    
    def install_modules(self) -> None:
        if not self.compiler:
            self.msg("error", "[!!] ERROR: Compiler is not installed [!!]")
            return
        self.msg("msg", f"Start Compiler: {self.name}")
        self.compiler.start()
        sleep(0.5)
        self.msg("msg", "------ Install Modules ------", sender=self.name)
        self.msg("msg", ", ".join(PY_LINUX_LIBRARY), sender=self.name)
        self.exec_cmd(f"cd /lab && source ./venv/bin/activate && pip install {' '.join(PY_LINUX_LIBRARY)}")
        self.msg("msg", "DONE", sender=self.name)
        self.msg("msg", "Stopping Compiler ......")
        self.compiler.stop()
    
    def default_commands(self, name: str, option: dict = {}) -> str:
        # compile to one file
        cmd = "--onefile "
        #set output path
        cmd += f"--distpath {self.dir_work}/{name}/dist "
        #set workpath 
        cmd += f"--workpath {self.dir_work}/{name}/build "
        #source file path
        cmd += f"{self.dir_work}/{name}/{name}.py"
        self.msg("dev", f"COMPILER CMD: {cmd}")
        return cmd

    def compile_pyinstaller(self, worm_pipeline: object) -> object:
        if not self.compiler:
            self.msg("error", "[!!] ERROR: I cannot compile the worm. Module missing. [!!]")
            return worm_pipeline
        self.msg("msg", f"Start Compiler: {self.name}")
        self.compiler.start()
        sleep(1)
        name = worm_pipeline.worm_name
        cmd = self.default_commands(name, worm_pipeline.gvar)
        self.exec_cmd(f"cd /lab && source ./venv/bin/activate && pyinstaller {cmd}")
        self.msg("msg", "Compile Done.", sender=self.name)
        self.msg("msg", "Cleaning files...", sender=self.name)
        self.exec_cmd(f"cp {self.dir_work}/{name}/dist/{name} {self.dir_work}/{name}/{name}")
        self.exec_cmd(f"chmod 777 {self.dir_work}/{name}/{name}")
        self.exec_cmd(f"rm -R {self.dir_work}/{name}/dist && rm -R {self.dir_work}/{name}/build")
        if worm_pipeline.gvar.get("USE_UPX"):
            self.msg("msg", "Start UPX", sender=self.name)
            self.exec_cmd(f"cd {self.dir_work}/{name} && upx -1 -v {name}")
        self.compiler.stop()
        worm_pipeline.exe_file_name = name
        worm_pipeline.exe_file_path = os.path.join(worm_pipeline.work_dir, worm_pipeline.exe_file_name)
        return worm_pipeline
    
    def compile_worm(self, worm_pipeline: object) -> object:
        if not self.compiler:
            self.msg("error", "[!!] ERROR: I cannot compile the worm. Module missing. [!!]")
            return worm_pipeline
        comp = worm_pipeline.gvar.get("COMPILER_NAME")
        match comp:
            case "LinPyIn":
                worm_pipeline = self.compile_pyinstaller(worm_pipeline)
            case _:
                self.msg("error", f"ERROR: No compiler: '{comp}'.", sender=self.name)
        return worm_pipeline





