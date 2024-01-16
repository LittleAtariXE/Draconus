import socket


class HttpAPI:
    def __init__(self, server_callback: object, preNumber : int = 4, admin_enable: bool = False):
        self.server = server_callback
        self.pre = str(preNumber)
        self.raw_len = self.server.raw_len
        self.format = self.server.format
        self.headers = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain; charset={self.format}\r\n\r\n"
        self.adminEnable = admin_enable
    
    def buildServer(self) -> bool:
        self.ip = self.server.ip
        self.port = self.pre + str(self.server.port)
        try:
            self.port = int(self.port)
            if self.port > 65535:
                self.server.Msg("[!!] ERROR HTTP SERVER: port number is bigger than 65535 [!!]")
                return False
        except (ValueError, TypeError) as e:
            self.server.Msg(f"[!!] ERROR HTTP SERVER: Wrong port number: {self.port}. Error: {e} [!!]")
            return False

        self.http = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.http.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            self.http.bind((self.ip, self.port))
            self.http.listen()
            return True
        except OSError as e:
            self.server.Msg(f"[!!] ERROR HTTP SERVER: bind address: {self.ip}:{self.port}. Error: {e} [!!]")
            return False
    
    def recive_request(self) -> str:
        msg = b""
        while True:
            recv = self.conn.recv(self.raw_len)
            if recv:
                if len(recv) < self.raw_len:
                    msg += recv
                    break
                msg += recv
            else:
                return None
        return msg.decode(self.format)
    
    def make_headers(self, content_len : int) -> str:
        head = f"HTTP/1.1 200 OK\r\nContent-Type: text/html; charset={self.format}\r\nContent-Length: {content_len}\r\n\r\n"
        return head
    
    def send_response(self, data : str) -> None:
        resp = self.make_headers(len(data)) + str(data)
        self.conn.sendall(resp.encode(self.format))
    
    def accept_conn(self) -> None:
        self.conn, self.addr = self.http.accept()
    
    def show_site(self, req : str) -> None:
        lines = req.split("\r\n")
        first_line = lines[0]
        first_line = first_line.split()
        match first_line[1]:
            case "/":
                self.send_response(self.home())
            case "/config":
                self.send_response(self.showConf())
            case "/conn":
                self.send_response(self.activeConn())
            case "/admin":
                self.send_response(self.admin())
            case "/pushStart":
                self.pushStart()
            case "/pushStop":
                self.pushStop()
    
    def response_content(self, content : str) -> str:
        response_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.server.name}_API HTTP</title>
</head>
<body>
    <h1><a href="http://{self.ip}:{self.port}/"><button type="button">BACK</button></a></h1>
    {content}
</body>
</html>
"""
        return response_content

    
    def home(self) -> str:
        home = f'<h1 align="center"> {self.server.name} Server </h1>'
        home += f'<h1><a href="http://{self.ip}:{self.port}/config">Server Config</a></h1>'
        home += f'<h1><a href="http://{self.ip}:{self.port}/conn">Active Connections</a></h1>'
        home += f'<h1><a href="http://{self.ip}:{self.port}/admin">Admin (Enable first in console)</a></h1>'
        home = self.response_content(home)
        return home
    
    def showConf(self) -> None:
        content = f"<h1> Server [{self.server.name}] Config</h1>"
        config = self.server.config
        for k,i in config.items():
            content += f"<h3>{k}  --  {i}</h3>"
        return self.response_content(content)
    
    def activeConn(self) -> None:
        content = f'<h1 align="center"> Active Connections</h1>'
        if not self.server.Central:
            content += '<h3>Server not listening</h3>'
            content += '<h3>No Connected Clients</h3>'
        else:
            for cli in self.server.Central.clients.values():
                content += f'<h3>{cli.ID} -- {cli.Addr} -- {cli.CliName} -- {cli.Os} --</h3>'
        return self.response_content(content)
    
    def admin(self) -> None:
        if not self.adminEnable:
            return self.response_content('<h1 align="center"> Admin is not enabled </h1>')
        response = '<h2 align="center"> Server Options </h2>'
        response += f'<h2><a href="http://{self.ip}:{self.port}/pushStart"><button type="button">Start Listening</button></a></h2>'
        response += f'<h2><a href="http://{self.ip}:{self.port}/pushStop"><button type="button">Stop Listening</button></a></h2>'
        return self.response_content(response)
    

    def pushStart(self) -> None:
        if self.adminEnable:
            self.server.listening()
        self.send_response(self.admin())
    
    def pushStop(self) -> None:
        if self.adminEnable:
            self.server.stopListening()
        self.send_response(self.admin())
    
    def __del__(self) -> None:
        self.http.close()


        


    def START(self) -> None:
        if not self.buildServer():
            return
        self.server.Msg(f"HTTP Server start. Address: http://{self.ip}:{self.port}")
        while True:
            self.accept_conn()
            while True:
                req = self.recive_request()
                if not req:
                    break
                self.show_site(req)
