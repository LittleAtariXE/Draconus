import os
import sys
import click
from click_shell import Shell
from termcolor import cprint

from .draco_shell import DracoShell


class MainShell:
    def __init__(self, commander_object: object):
        self.COM = commander_object

    def Run(self) -> None:
        if not self.COM.Start():
            sys.exit()
        self.draco_shell = DracoShell(self, self.COM)
        self.draco_shell.Run()
    
    def exit_shell(self, *args, **kwargs) -> None:
        print("EXIT SHELL PROGRAM")
    
    def sorter(self, name: str, info: str, cname: str ="blue", cinfo: str = "green"):
        sep = 35
        cprint(f"\t{name}", cname, end="")
        cprint(f"{'':{sep - len(name)}}{info}", cinfo)
    
    
