import os
from jinja2 import Template
from typing import Union





class MrComp:
    def __init__(self, comp_library: object, master_compiler: object, worm_var: dict, worm_global_var: dict):
        self.name = "MrComp"
        self.Lib = comp_library
        self.master_compiler = master_compiler
        self.worm_var = worm_var
        self.worm_gvar = worm_global_var
        self.msg = self.Lib.msg
        self.default_script = {
            "WinePyInst" : "PyInstall"
        }
        self._var = {}
        self._item = None

    @property
    def var(self) -> dict:
        var = self.default_var()
        item = self.load_item()
        if item:
            var.update(item.setVar)
        var.update(self._var)
        return var

    def extract_var(self) -> dict:
        cvar = {}
        for name, var in self.worm_var.items():
            if name.startswith("_COMP_"):
                cvar[name[6:]] = var
        return cvar
    
    def load_item(self) -> Union[object, None]:
        name = self.default_var()["SCRIPT_NAME"]
        item = self.Lib.get_item("comp_script", name)
        if not item:
            return None
        self._item = item
        return item
    
    def set_var(self, name: str, value: any) -> None:
        self._var[name] = value
    


    def default_var(self) -> dict:
        opt = {}
        # Worm icon
        icon = self.worm_gvar["ICON"]
        if not icon:
            opt["ICON"] = ""
        else:
            opt["ICON"] = os.path.basename(icon)
        # Use default UPX
        opt["UPX"] = True
        # Console or windows app
        if self.worm_gvar["PROGRAM_TYPE"] == "window":
            opt["CONSOLE"] = False
        else:
            opt["CONSOLE"] = True
        # compiler name
        opt["COMPILER_NAME"] = self.worm_gvar["COMPILER_NAME"]
        # set script
        opt["SCRIPT_NAME"] = self.default_script.get(opt["COMPILER_NAME"])

        opt.update(self.extract_var())
        return opt
    
    def render_compile_script(self, conf: dict = {}) -> Union[str, None]:
        if not self._item:
            self.load_item()
        if not self._item:
            self.msg("error", "ERROR: A compilation script cannot be created. No item.", sender=self.name)
            return None
        code = self._item.raw_code
        code = Template(code)
        var = self.var.copy()
        var.update(conf)
        code = code.render(var)
        return code
    
    def save_script(self, name: str, worm_pipeline: object, extra_conf: dict = {}) -> bool:
        fpath = os.path.join(worm_pipeline.work_dir, name)
        data = self.render_compile_script(extra_conf)
        if not data:
            return False
        try:
            with open(fpath, "w") as file:
                file.write(data)
            return True
        except Exception as e:
            self.msg("error", f"[!!] ERROR Save compilation script: {e} [!!]", sender=self.name)
            return False
    
    def build_exclude_mods_list(self, fpath: str) -> str:
        self.msg("msg", "Exclude libraries from the executable file. It may take a while ...", sender=self.name)
        comp = self.master_compiler.main_comp.get("WinePy")
        if not comp:
            self.msg("error", "[!!] ERROR: No compiler 'WinePy' [!!]")
            return "[]"
        # self.msg("msg", "Exclude modules:", sender=self.name)
        excludes = comp.exe_command(f"cd /library && wine python modulator.py {fpath}")
        return excludes

    def make_pyinstaller_script(self, worm_pipeline: object, extra_conf: dict = {}) -> object:
        name = f"{worm_pipeline.worm_name}.spec"
        worm_pipeline.comp_script_name = name
        if worm_pipeline.gvar.get("PYINSTALLER_EXCLUDE_MODS"):
            docker_path = os.path.join("/hive", worm_pipeline.worm_name, worm_pipeline.file_name)
            excludes = self.build_exclude_mods_list(docker_path)
        else:
            excludes = []
        econf = {
            "_WORM_NAME" : os.path.basename(worm_pipeline.code_file_path),
            "EXE_NAME" : worm_pipeline.worm_name,
            "EXCLUDE_MODS" : excludes
        }
        
        if not self.save_script(name, worm_pipeline, econf):
            self.msg("msg", "Use standard build")
            self.worm_pipeline.pre_compile = False
            return worm_pipeline
        self.msg("msg", f"Prepare script done.", sender=self.name)
        return worm_pipeline

    def make_script(self, worm_pipeline: object) -> object:
        comp = worm_pipeline.gvar.get("COMPILER_NAME")
        if not comp:
            self.msg("error", "ERROR: Compiler not set !! Skip step.", sender=self.name)
            return worm_pipeline
        match comp:
            case "WinePyInst":
                return self.make_pyinstaller_script(worm_pipeline)
            case _:
                self.msg("msg", f"WARNING: No compilation script for '{comp}'. Skip step.", sender=self.name)
        return worm_pipeline


        

   