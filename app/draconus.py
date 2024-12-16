import sys
import os
import threading
from time import sleep

from .tools.messanger import Messenger
from .tools.super_visor import SuperVisor
from .conn.ctrl_conn import ControlConnector
from .conn.central import Central
from .controlers.server_control import ServerControler
from .storage.storekeeper import Storekeeper



class Draconus:
    def __init__(self, builder_object: object, options: dict = {}):
        self._ext_conf = options
        self.working_FLAG = threading.Event()
        self.working_FLAG.clear()
        self.config = builder_object
        # self.config.make_dirs()
    

    def lock_draco(self) -> bool:
        if os.path.exists(self.config.draco_lock_file):
            print("[!!] ERROR: Draconus propably is running. Check Process list. [!!]")
            print("[!!] if not try run with option: '--force' [!!]")
            print("ex: 'python3 Draconus.py --force'")
            return False
        else:
            with open(self.config.draco_lock_file, "w") as file:
                file.write(str(os.getpid()))
            return True
    
    def check_start(self) -> bool:
        if self._ext_conf.get("FORCE_RUN"):
            with open(self.config.draco_lock_file, "w") as file:
                file.write(str(os.getpid()))
        else:
            if not self.lock_draco():
                return False
        return True

    
    def cleaner(self) -> None:
        too_clean = [self.config.draco_lock_file, self.msg.fd_path, self.config.socket_draco_ctrl]
        for tc in too_clean:
            if os.path.exists(tc):
                try:
                    os.unlink(tc)
                except:
                    pass
        
    def build(self) -> bool:
        self.working_FLAG.set()
        self.msg = Messenger(self.config, "Draconus")
        self.msg.START()
        self.Task = SuperVisor(self)
        self.Task.Start()
        self.ctrl_conn = ControlConnector(self)
        if not self.ctrl_conn.Start():
            self.msg("error", "[!!] ERROR: Cant start Draconus. Exit Program [!!]")
            return False
        self.Storage = Storekeeper(self)
        self.Central = Central(self)
        self.ServerCtrl = ServerControler(self)
        return True

    def work(self) -> None:
        if not self.check_start():
            sys.exit()
        if not self.build():
            self.Exit()
    
    def _shutdown(self) -> None:
        self.Central.close_central()
        self.working_FLAG.clear()
        sleep(1)
        self.msg("msg", "Draconus Stopped")
        self.cleaner()
        sleep(0.2)
    
    def Start(self) -> None:
        if not self.check_start():
            return
        if self.build():
            self.msg("msg", "Draconus Started")
            while self.working_FLAG.is_set():
                sleep(1)
        else:
            self.Exit()
            
    def Exit(self) -> None:
        self._shutdown()
        print("EXIT PROGRAM")
        sys.exit()


