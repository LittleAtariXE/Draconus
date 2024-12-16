import docker
import os
from time import sleep
from typing import Union

from app.hive.etc.py_lib import PY_LIBRARY

class CrossCythonCore:
    def __init__(self, master: object):
        self.master = master
        self.msg = self.master.queen.msg
        self.name = "CrossCy"
        self.dir_hive = self.master.queen.dir_hive_out
        self.dir_work = "/hive"
        self.dir_etc = os.path.join(os.path.dirname(__file__), "etc")
        self.dir_lab_lib = "/library"
        self.dir_lab = "/lab"


        self.master_system_compiler = "ubuntu:latest"
        self.compiler_container_name = "cross_cython"
        self.docker = docker.from_env()
        self._container_id = None

        self._win = True
        self._linux = False
    
    @property
    def config(self) -> dict:
        conf = {
            "python312.dll" : f"{self.dir_lab_lib}/lib/python312.dll",
            "python312.def" : f"{self.dir_lab_lib}/lib/python312.def",
            "include_win" : f"{self.dir_lab_lib}/lib/include.tar",
            "libpython" : f"{self.dir_lab_lib}/lib/libpython3.12.dll.a"
        }
        return conf
    
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
                self.msg("msg", f"Status: {line['status']}")
            if 'progress' in line:
                self.msg("msg", f"Progress: {line['progress']}")
            if 'id' in line:
                self.msg("msg", f"ID: {line['id']} - {line['status']} {line.get('progress', '')}")
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
        self.msg("msg", "Start image downloads. This may take some time.")
        sleep(1)
        self.pull_image_with_progress(self.master_system_compiler)
        self.msg("msg", "Get image...")
        if not self.compiler:
            self.msg("error", f"[!!] ERROR '{self.name}': building compiler [!!]")
            return
        print("INSTALL DONE")
        self.build_lab()
    
    def build_lab(self) -> None:
        self.msg("msg", "[!!] Start of laboratory construction .... [!!]", sender=self.name)
        self.compiler.start()
        sleep(1)
        self.exec_cmd(f"mkdir {self.dir_lab}")
        self.exec_cmd(f"cp {self.config['python312.dll']} {self.dir_lab}/python312.dll")
        self.exec_cmd(f"chmod 777 {self.dir_lab}/python312.dll")
        self.exec_cmd(f"cp {self.config['python312.def']} {self.dir_lab}/python312.def")
        self.exec_cmd(f"cp {self.config['include_win']} {self.dir_lab}/include.tar")
        self.exec_cmd(f"cd {self.dir_lab} && tar -xvf include.tar")
        self.exec_cmd(f"cp {self.config['libpython']} {self.dir_lab}/libpython3.12.dll.a")
        self.exec_cmd(f"ls -la {self.dir_lab}")
        self.exec_cmd("apt update")
        self.exec_cmd("apt install -y mingw-w64 gcc-mingw-w64 g++-mingw-w64 binutils-mingw-w64 build-essential make pkg-config")
        self.msg("msg", "----- INSTALL PYTHON and CYTHON ------")
        sleep(1)
        self.exec_cmd("apt install -y python3 python3-pip python3-dev")
        self.exec_cmd("apt install -y cython3")
        self.compiler.stop()
        self.msg("msg", f"[{self.name}] is ready.")
    
    def install_modules(self) -> None:
        if not self.compiler:
            self.msg("error", "[!!] ERROR: I cannot compile the worm. Module missing. [!!]")
            return
        self.msg("msg", f"Start Compiler: {self.name}")
        self.compiler.start()
        sleep(0.5)
        self.msg("msg", "------ Install Modules ------", sender=self.name)
        self.msg("msg", ", ".join(PY_LIBRARY), sender=self.name)
        self.exec_cmd("apt update")
        for mod in PY_LIBRARY:
            self.exec_cmd(f"apt install -y python3-{mod}")
        self.msg("msg", "DONE", sender=self.name)
        self.msg("msg", "Stopping Compiler ......")
        self.compiler.stop()

    
    # def compile_worm(self, name: str, option: dict = {}) -> None:
    #     if not self.compiler:
    #         self.msg("error", "[!!] ERROR: I cannot compile the worm. Module missing. [!!]")
    #         return
    #     self.msg("msg", f"Start Compiler: {self.name}")
    #     self.compiler.start()
    #     sleep(1)
    #     worm_path = os.path.join(self.dir_hive, name, f"{name}.py")
    #     self.exec_cmd(f"cd {self.dir_work}/{name} && cython --embed -o {name}.c {name}.py")
    #     sleep(0.2)
    #     self.exec_cmd(f"cd {self.dir_work}/{name} && x86_64-w64-mingw32-gcc -I/lab/include -L/lab {name}.c -o {name}.exe -lpython312 -municode -Wl,-subsystem,console")
    #     # self.exec_cmd(f"cd {self.dir_work}/{name} && x86_64-w64-mingw32-gcc -I/lab/include -L/lab {name}.c -o {name}.exe -lpython312 -municode -Wl,-subsystem,windows")
    #     self.msg("msg", "If you don't see any errors it means the Worm is ready", sender=self.name)
    #     self.msg("msg", "Stopping Compiler ......")
    #     self.compiler.stop()
    
    def compile_worm(self, worm_pipeline: object) -> object:
        if not self.compiler:
            self.msg("error", "[!!] ERROR: I cannot compile the worm. Module missing. [!!]")
            return worm_pipeline
        return self.compile_exe_app(worm_pipeline)
        
    def compile_exe_app(self, worm_pipeline: object) -> object:
        self.msg("msg", f"Start Compiler: {self.name}")
        worm_name = worm_pipeline.worm_name
        self.compiler.start()
        sleep(1)
        self.exec_cmd(f"cd {self.dir_work}/{worm_name} && cython3 --embed -o {worm_name}.c {worm_name}.py")
        sleep(0.2)
        self.exec_cmd(f"cd {self.dir_work}/{worm_name} && x86_64-w64-mingw32-gcc -I/lab/include -L/lab {worm_name}.c -o {worm_name}.exe -lpython312 -municode -Wl,-subsystem,console")
        # self.exec_cmd(f"cd {self.dir_work}/{worm_name} && x86_64-w64-mingw32-gcc -I/lab/include -L/lab {worm_name}.c -o {worm_name}.exe -lsteam.a -municode -Wl,-subsystem,console")
        self.msg("msg", "If you don't see any errors it means the Worm is ready", sender=self.name)
        self.msg("msg", "Stopping Compiler ......")
        self.compiler.stop()
        worm_pipeline.exe_file_path = os.path.join(worm_pipeline.work_dir, f"{worm_name}.exe")
        print("EXE_PATH: ", worm_pipeline.exe_file_path)

        
        return worm_pipeline



##### x86_64-w64-mingw32-gcc -I/lab/include -L/lab myscript.c -o myscript.exe -lpython3.12 -municode -Wl,-subsystem,console
### x86_64-w64-mingw32-gcc -shared -o mymodule.pyd -I/lab/include mymodule.c -lpython3.12 -L<ścieżka_do_lib_pythona>
### x86_64-w64-mingw32-gcc -shared -o kkk.pyd -I/lab/include -L/lab kkk.c -lpython3.12
