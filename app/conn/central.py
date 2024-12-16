from time import sleep
from threading import Lock
from typing import Union
from threading import Event
from .protocols.tcp_handler import TcpHandler
from .protocols.tcp_rawhandler import TcpRawHandler
from .protocols.tcp_rawdown import TcpRawDownloader
from .protocols.tcp_send import TcpRawSend
from .servers.tcp_server import Server
from .servers.sender import Sender
from .servers.raw_sender import RawSendHandler


class ClientHandler:
    def __init__(self, client_ID: str, conn_obj: object, addr: object, central_callback: object, server_name: str, protocol: object):
        self.ID = client_ID
        self.conn = conn_obj
        self.addr = addr
        self.ip = self.addr[0]
        self.central = central_callback
        self.client = f"<{self.ID}><{self.addr[0]}:{self.addr[1]}>"
        self.handler_FLAG = Event()
        self.handler_FLAG.set()
        self.server_name = server_name
        self.signal_close = False
        self.info = {
            "system" : "unknown"
        }
        self.handler = protocol(
            self.central.draco.working_FLAG,
            self.handler_FLAG,
            self.conn,
            self.central.raw_len,
            self.central.format_code,
            self.central.separator,
            self.central.socket_to
        )

    
    def recive_msg(self) -> None:
        while self.handler_FLAG.is_set():
            recv = self.handler.recive_data()
            if not recv:
                break
            self.central.handle_incoming_data(self, recv)
        self.close()
    
    def send_msg(self, data: dict) -> None:
        self.handler.send_data(data)
    
    def send_raw(self, data: dict) -> None:
        cmd = data.get("data")
        if not cmd:
            return
        try:
            self.handler.conn.send(cmd.encode(self.central.format_code))
        except Exception as e:
            print("RAW ERROR: ", e)



    
    def close(self) -> None:
        if self.signal_close:
            return
        self.signal_close = True
        self.handler_FLAG.clear()
        try:
            self.conn.close()
        except:
            pass
        self.central.msg("no_imp", f"Close Connection: {self.client}", sender=self.server_name)
    
    def client_data(self) -> str:
        data = f"--------------- Client: {self.client} -------------------\n"
        data += f"SYSTEM: {self.info.get('system')}\n"
        for k, i in self.info.items():
            data += f"-- {k} ----- {i}\n"
        return data



class Central:
    def __init__(self, draco_callback: object):
        self.draco = draco_callback
        self.msg = self.draco.msg
        self.raw_len = self.draco.config.tcp_socket_raw_len
        self.format_code = self.draco.config.tcp_socket_format
        self.separator = self.draco.config.tcp_socket_separator
        self.socket_to = self.draco.config.tcp_sock_to_recive
        self.clean_pause = self.draco.config.central_clean_pause
        self.client_ID = 0
        # {"NAME" : {clients: {id : handler}, server: server}}
        self.servers = {}
        self.clients = {}
        self.lock = Lock()
        self.msg("dev", "Central is Ready")
        self.draco.Task.add_task("Central Cleaner", self.cleaning, info="Clean no active connections")
        self.protocols = {
            "TcpHandler" : TcpHandler,
            "TcpRawHandler" : TcpRawHandler,
            "TcpRawDownloader" : TcpRawDownloader,
            "TcpRawSend" : TcpRawSend
        }

    

    def add_connection(self, conn_obj: object, addr: object, server_name: str, protocol_type: str) -> None:
        with self.lock:
            self.client_ID += 1
            client_id = str(self.client_ID)
        protocol = self.protocols.get(protocol_type)
        if not protocol:
            self.msg("error", "[!!] ERROR: Unknown Protocol. Use 'TcpRawProtocol' [!!]" )
            protocol = self.protocols["TcpRawHandler"]
        cli = ClientHandler(client_id, conn_obj, addr, self, server_name, protocol)
        with self.lock:
            self.clients[client_id] = cli
        if protocol_type == "TcpRawSend":
            raw_sender = RawSendHandler(self.draco, cli)
            raw_sender.start()
            self.draco.Task.add_ready_task(f"Handler-{client_id}", raw_sender, "Send file to client")
            return
        self.draco.Task.add_task(f"Handler-{client_id}", cli.recive_msg, info=f"Client handler no. {client_id} from server: {server_name}.")
        self.msg("msg", f"New Connection from: {cli.client}")
    
    def build_server(self, data: dict) -> None:
        if not data.get("name"):
            self.msg("error", "[!!] Missing config: server name [!!]")
            return
        name = data.get("name")
        try:
            port = int(data.get("port"))
        except ValueError as e:
            self.msg("error", f"[!!] ERROR Port Number: {e} [!!]")
            return
        if name in self.servers.keys():
            self.msg("error", f"[!!] ERROR: Server with this name exists [!!]")
            return
        options = {"PROTOCOL_TYPE" : data.get("PROTOCOL_TYPE", "default")}
        serv = Server(self.draco, name, port, options)
        serv.start()
        sleep(1)
        if serv.build_FLAG:
            self.servers[name] = serv
            self.draco.Task.add_ready_task(f"Server-{name}", th_object=serv, info=f"Server {name} on port: {port} - Main Thread")
    
    def close_server(self, name: str) -> None:
        server = self.servers.get(name)
        if not server:
            self.msg("error", f"[!!] ERROR: Server '{name}' not exists [!!]")
            return
        server.close()
        # sleep(1)
        del self.servers[name]
        

    def close_central(self) -> None:
        self.msg("msg", "Close Clients and Servers")
        for c in self.clients.values():
            c.close()
        for s in self.servers.values():
            s.close()
        sleep(0.5)

    def cleaning(self) -> None:
        while self.draco.working_FLAG.is_set():
            too_clean = []
            with self.lock:
                for cli in self.clients.values():
                    if not cli.handler_FLAG.is_set():
                        too_clean.append(cli.ID)
                for c in too_clean:
                    try:
                        del self.clients[c]
                    except KeyError:
                        pass
            sleep(self.clean_pause)
    
    def get_client(self, client_id: str) -> Union[object, None]:
        client = self.clients.get(client_id)
        if not client:
            self.msg("error", f"[!!] ERROR: client id: {client_id} is not connected [!!]")
            return None
        else:
            return client
    
    def send_msg(self, client_id: str, data: dict) -> None:
        client = self.get_client(client_id)
        if not client:
            return
        client.send_msg(data)
    
    def send_raw(self, client_id: str, data: dict) -> None:
        print("DATA: ", data)
        client = self.get_client(client_id)
        if not client:
            return
        client.send_raw(data)
    
    def send_file(self, client_id: str, fname: str) -> None:
        cli = self.get_client(client_id)
        if not cli:
            return
        self.msg("no-imp", f"start send file: {fname}")
        send = Sender(self.draco, cli)
        send.set_params(fname)
        send.start()

    
    def send_client_to_commander(self, client_id: str) -> None:
        cli = self.get_client(client_id)
        if not cli:
            data = "None"
        else:
            data = {
                "id" : cli.ID,
                "server_name" : cli.server_name,
                "client_name" : cli.client
            }
        self.draco.ctrl_conn.send_data(data)
    
    def handle_incoming_data(self, client_object: object, recv_data: Union[bytes, str, list, dict]) -> None:
        # Flags:
        # RAW_MSG - only simple messages
        # NO_MSG - messages from the client will not be displayed
        # RAW_DOWNLOAD - Simple download through the main channel
        # EXEC_CMD - JSON encoded messages containing cooperative commands

        FLAG = client_object.handler.conn_FLAG
        
        if "RAW_DOWNLOAD" in FLAG:
            self.draco.Storage.take_delivery(recv_data, handler=client_object)
            return
        if "NO_MSG" in FLAG:
            return
        elif "EXEC_CMD" in FLAG:
            self.draco.ServerCtrl.check_cmd(recv_data, client_object)
            return
        elif "RAW_MSG" in FLAG:
            try:
                msg = recv_data.decode(self.format_code)
            except:
                msg = recv_data
        self.msg("msg", f"RAW message: {msg}", sender=client_object.client)
           


    
    
    def show_servers(self) -> None:
        cli_num = {}
        servers = {}
        for sname, serv in self.servers.items():
            if not sname in cli_num.keys():
                cli_num[sname] = 0
            servers[sname] = serv._options.get("PROTOCOL_TYPE", "default")
        for cli in self.clients.values():
            cli_num[cli.server_name] += 1
        
        text = "\n-------------------------------- Active Servers: ------------------------------------------\n"
        text +=f"{'Server Name:':<25}{'Server Type:':<20}Connected clients:\n"
        for name, stype in servers.items():
            text += f"-- {name:<25} --{stype:<20}{cli_num[name]}\n"
        self.msg("msg", text)

    
    def show_clients(self) -> None:
        text = "\n" + "-" * 30 + " Connected Clients: " + "-" * 30 + "\n"
        text += f"{'ID, address':<35}{'System:':<35}Server name:\n"
        for cli in self.clients.values():
            text += f"{cli.client:<35}{cli.info['system']:<35}{cli.server_name}\n"
        self.msg("msg", text)
