
from multiprocessing import Pipe
from time import sleep


class ServerHandler:
    def __init__(self, name: str, pipe: Pipe, server: object, draco_callback: object):
        self.name = name
        self.pipe = pipe
        self.server = server
        self.draco = draco_callback
        self.working = False
    
    def sendCmd(self, cmd: list) -> None:
        try:
            self.pipe.send(cmd)
        except BrokenPipeError as e:
            self.draco.Msg(f"[!!] ERROR: send command to server [!!] : {e}")
    
    def reciveData(self) -> list:
        check = self.pipe.poll(timeout=3)
        if not check:
            return None
        if check:
            recv = self.pipe.recv()
            return recv
    
    def begin(self) -> None:
        self.draco.Msg(f"Server <{self.name}> install successfull ... try starting...")
        self.server.start()
        sleep(0.5)
        resp = self.reciveData()
        if not resp:
            self.draco.Msg(f"Server <{self.name}> not working. Check log files")
        elif resp == ["OK"]:
            self.working = True
        
