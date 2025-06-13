import os
import subprocess


class Loader:
    def __init__(self):
        self.dir_main = os.path.dirname(__file__)
        self.file_shell = os.path.join(self.dir_main, "Commander.py")
        self.dir_venv = os.path.join(self.dir_main, "venv")
        self.venv_activate = os.path.join(self.dir_venv, "bin", "activate")
        self.check_venv = os.path.exists(self.dir_venv)
        self.file_req = os.path.join(self.dir_main, "requirements.txt")
    
    def enter_venv(self) -> bool:
        if not self.check_venv:
            try:
                print("[LOADER] Build venv .....")
                os.system(f"python3 -m venv {self.dir_venv}")
            except Exception as e:
                print(f"[LOADER] ERROR build venv: {e}")
                return
            try:
                print("[LOADER] Install requirements ....")
                os.system(f"{os.path.join(self.dir_venv, 'bin', 'pip')} install -r {self.file_req}")
            except Exception as e:
                print(f"[LOADER] ERROR install pip package: {e}")
                return
        
        return True
    
    def load(self) -> None:
        if not self.enter_venv():
            return
        print("[LOADER] Start Commander")
        try:
            out = subprocess.run(f"source {self.venv_activate} && python3 {self.file_shell}", shell=True, executable="/bin/bash")
        except Exception as e:
            print(f"[LOADER] ERROR: {e}")

if __name__ == "__main__":
    load = Loader()
    load.load()
