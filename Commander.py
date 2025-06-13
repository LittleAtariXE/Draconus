from app.tools.builder import Builder
from app.cc.commander import Commander
from app.shell.main import MainShell
     

if __name__ == "__main__":
    CC = Commander(Builder())
    shell = MainShell(CC)
    shell.Run()
