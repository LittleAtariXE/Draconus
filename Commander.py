import sys
from app.tools.builder import Builder
from app.cc.commander import Commander
from app.shell.main import MainShell


def start_queen(args) -> bool:
    if len(args) > 1:
        if args[1] == "queen":
            return True
        else:
            return False
    return False

if __name__ == "__main__":
    only_queen = start_queen(sys.argv)
    CC = Commander(Builder(), only_queen)
    shell = MainShell(CC)
    shell.Run()