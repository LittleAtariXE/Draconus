import os
import click
from click_shell import shell
from termcolor import cprint
from time import sleep


class ClientShell:
    def __init__(self, commander: object, client_data: dict):
        self.COM = commander
        self.cli_id = client_data.get("id")
        self.server_name = client_data.get("server_name")
        self.client_name = client_data.get("client_name")
    
    def exit_client_shell(self, *args, **kwargs) -> None:
        cprint("[Draconus] Exit Client Shell", "yellow")
    
    def sorter(self, name: str, info: str, cname: str ="blue", cinfo: str = "yellow"):
        sep = 35
        cprint(f"\t{name}", cname, end="")
        cprint(f"{'':{sep - len(name)}}{info}", cinfo)


    def build(self) -> object:

        @shell(prompt=f"[{self.server_name}][{self.client_name}] >>", intro="------ Client Shell ------- ", on_finished=self.exit_client_shell)
        def cliShell() -> None:
            pass

        @cliShell.command()
        def help():
            cprint("\n------------------------------ Client Command ----------------------------------\n", "blue")
            self.sorter("msg [command] [data]", "Send message, command to client. See 'msg --help'")
            self.sorter("send [file_name]", "Sending file to client. The file must be in the IN directory.")
            self.sorter("raw [command]", "Sending a simple (raw) message to client. For simple communication.")
            self.sorter("exit", "Back to Draconus shell")
        
        @cliShell.command()
        @click.argument("command")
        @click.argument("data", default="")
        def msg(command, data):
            """\nSends commands to the client if the client has TCP communication with headers. Put long commands containing spaces in quotation marks “”.
    To view a list of worm commands, type the command: “msg help”.\n
    ex: msg powershell "dir"\n
    ex: msg cmd "ipconfig /all"\n
    ex: msg help\n"""
            if command:
                cdata = {"cmd" : command, "data" : data}
                self.COM.send_CMD("server", "msg", cdata, cli_id=self.cli_id)


        @cliShell.command()
        @click.argument("text")
        def raw(text):
            """\nIt sends a raw message to the client without headers and coding.
    If the client has an advanced communication method then it will not read this message. """
            if text:
                data = {"data" : text}
                self.COM.send_CMD("server", "raw", data, cli_id=self.cli_id)
        
        @cliShell.command()
        @click.argument("name")
        def send(name):
            """\nIt sends the file to the client.
    The file must be in the 'IN' directory which is located in the root directory of Draconus. The client must support the ability to receive files.\n
    ex: send "my_file.exe"\n"""
            if name:
                data = {"cli_id" : self.cli_id, "fname" : name}
                self.COM.send_CMD("server", "send", data)
                

        return cliShell
    
    def Run(self) -> None:
        shell = self.build()
        sleep(0.2)
        shell()
