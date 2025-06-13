import os
import click
from click_shell import shell
from termcolor import cprint
from time import sleep

from .queen_shell import QueenShell
from .client_shell import ClientShell

HELP_SERVER_TYPES = """
\nTypes of servers you can create:\n
'default' - Default. Does not require a type. TCP server. Sends and receives messages in base64 encoded JSON. Can send and receive multiple files at once, receives commands from the worm.\n
'raw' - TCP server. Sends and receives messages without any coding etc. Perfect for simple communication.\n
'down' - Simple TCP server for receiving files. Accepts a connection and immediately receives the file, then disconnects the client. The downloaded files are located in the 'OUTPUT/LOOT/DUMP' directory\n
'send' - Server TCP only for uploading files. When a client connects it automatically sends files to it. After the server is created, a directory with the server name will appear in the 'IN' directory, place the files to be sent there.\n
'b64' - Server TCP. Sends and receives base64 encoded messages.\n
\n
"""


class DracoShell:
    def __init__(self, main_shell: object, commander: object):
        self.main  = main_shell
        self.COM = commander
        self.sort = self.main.sorter
    

    def build(self) -> object:

        @shell(prompt=f"[DRACONUS] >>", intro="------ Welcome To Draconus ! Put help for commands list ------- ", on_finished=self.main.exit_shell)
        def dracoShell() -> None:
            pass

        @dracoShell.command()
        def help() -> None:
            cprint("\n------------------------------ Draconus Command ----------------------------------\n", "blue")
            self.sort("clr, clear", "Clear Screen")
            self.sort("exit", "Exit Shell. Draconus still working")
            self.sort("quit", "Close Draconus")
            self.sort("task", "Show Active Task/Threads")
            self.sort("server [name] [port]", "Making TCP Listener Server")
            self.sort("close [name]", "Close Server")
            self.sort("show -[option]", "Show active servers and connected clients. See 'show --help'")
            self.sort("conn [client_id]", "Enter the client connection console.")
            self.sort("hive", "Enter to Hive Shell")
            cprint("\n\n\nSome commands have a help. ex: 'server --help'\n", "yellow")
        
        @dracoShell.command()
        def clr() -> None:
            os.system("clear")
        
        @dracoShell.command()
        def clear() -> None:
            os.system("clear")

        @dracoShell.command()
        def quit() -> None:
            self.COM.send_CMD("sys", "quit")
            sleep(3)
            self.main.exit_shell()
            os._exit(0)
        
        @dracoShell.command()
        def task() -> None:
            self.COM.send_CMD("sys", "task")
        
        
        @dracoShell.command()
        @click.argument("name")
        @click.argument("port")
        @click.option("--types", "-t", required=False, help=HELP_SERVER_TYPES)
        def server(name, port, types) -> None:
            """\n\tname  --  Server Name\n\n\tport  --  Server Port. Bigger than 1999"""
            data = {"name" : name, "port" : port}
            if types:
                data.update({"PROTOCOL_TYPE" : types})
            self.COM.send_CMD("server", "make", data)
        
        @dracoShell.command()
        @click.argument("name")
        def close(name) -> None:
            """\n\tname  --  Server name\n"""
            self.COM.send_CMD("server", "close", name)
        
        @dracoShell.command()
        @click.option("--server", "-s", required=False, is_flag=True, help="Show active servers")
        @click.option("--client", "-c", required=False, is_flag=True, help="Show connected clients")
        def show(server, client):
            if server:
                self.COM.send_CMD("server", "show_server")
            if client:
                self.COM.send_CMD("server", "show_client")
            
        
        @dracoShell.command()
        def hive() -> None:
            hive_shell = QueenShell(self.main, self.COM)
            hive_shell.Run()
        
        @dracoShell.command()
        @click.argument("client_id")
        def conn(client_id):
            if client_id:
                self.COM.send_CMD("server", "client", client_id)
                response = self.COM.recive_data()
                if response == "None":
                    return
                else:
                    client = ClientShell(self.COM, response[0])
                    client.Run()


        return dracoShell
    
    def Run(self) -> None:
        shell = self.build()
        sleep(0.5)
        shell()