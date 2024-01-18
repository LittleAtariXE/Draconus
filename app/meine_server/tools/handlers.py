import socket

from threading import Lock, Thread

class MrHandler:
    def __init__(self, cli_ID: str, conn: object, addr: object, central_callback : object):
        self.ID = cli_ID
        self.conn = conn
        self.addr = addr
        self.Addr = f"{self.addr[0]}:{self.addr[1]}"
        self.central = central_callback
        self.is_conn = True
        self.sysHead = self.central.server.sysHeadears
        self.Os = "Unknown"
        self.EnvVar = "Unknown"
        self.CliName = "Unknown"
    
    def updateInfo(self, info: list) -> None:
        self.CliName = info[0]
        self.Os = info[1]
        self.EnvVar= info[2]

    def sendMsg(self, msg : str) -> None:
        try:
            msg = self.central.Cham.encrypt(msg)
            self.conn.sendall(msg)
        except (OSError, BrokenPipeError, TimeoutError) as e:
            self.central.Msg(f"[!!] ERROR: send msg to client: {self.ID} : {e}")
    
    def reciveMsg(self) -> str:
        msg = b""
        while True:
            try:
                recv = self.conn.recv(self.central.server.raw_len)
            except (ConnectionRefusedError, ConnectionAbortedError, ConnectionResetError):
                return None
            if not recv:
                return None
            else:
                if len(recv) < self.central.server.raw_len:
                    msg += recv
                    break
                else:
                    msg += recv
        msg = self.central.Cham.decrypt(msg)
        return msg
    
    def wait4msg(self) -> None:
        self.conn.settimeout(3)
        while self.central.server.is_listening:
            try:
                msg = self.reciveMsg()
            except socket.timeout:
                continue
            except (BrokenPipeError, ConnectionRefusedError, ConnectionAbortedError):
                break
            if not msg:
                break
            else:
                if msg.startswith(self.sysHead):
                    self.central.server.Ctrl._sysCMD(msg, self)
                else:
                    self.central.Msg(msg, sender=self.Addr)
        self.is_conn = False
  
    def __del__(self) -> None:
        self.conn.close()
    
    def START(self) -> None:
        self.wait4msg()
        self.central.Msg("Close Connection", sender=self.Addr, dev=True)
        self.conn.close()

        
    


class ConnCentral:
    def __init__(self, server_callback : object, msg_callback : object, chameleon : object):
        self.server = server_callback
        self.Cham = chameleon
        self.Msg = msg_callback
        self.cliID = 0
        self.clients = {}
        self.lock = Lock()

    def addClient(self, conn : object, addr : object) -> object:
        with self.lock:
            self.cliID = self.cliID + 1
            new = str(self.cliID)
        client = MrHandler(new, conn, addr, self)
        self.clients[new] = client
        self.server.Tasker.addTask(name=f"Handler-{client.ID}", func_name=client.START, info=f"Handler Client no: {client.ID}. Addr: {client.Addr}", types="handlers")
        self.Msg(f"New connection from: {client.Addr}", noI=True)
        return client
    
    def showClient(self) -> None:
        buff = "ALL CONNECTIONS:\n"
        for client in self.clients.values():
            buff += f"\n{client.ID}  -- {client.Addr} -- {client.CliName} -- {client.Os} --"
        self.Msg(buff)
      
    
    def clear(self) -> None:
        too_del = []
        for cli, connObj in self.clients.items():
            if not connObj.is_conn:
                too_del.append(cli)
        for c in too_del:
            del self.clients[c]
        


