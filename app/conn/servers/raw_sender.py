import os
from threading import Thread
from typing import Union
from time import sleep


class RawSendHandler(Thread):
    def __init__(self, draconus: object, handler: object):
        super().__init__(daemon=True)
        self.draco = draconus
        self.msg = self.draco.msg
        self.handler = handler
        self.name = self.handler.server_name
        self.dir_in = self.draco.config.dir_in
        self.dir_input = os.path.join(self.dir_in, self.name)
        if not os.path.exists(self.dir_input):
            os.mkdir(self.dir_input)
    
    def find_files(self) -> Union[None, list]:
        files = []
        for f in os.listdir(self.dir_input):
            if os.path.isdir(f):
                continue
            files.append(os.path.join(self.dir_input, f))
        if len(files) < 1:
            return None
        else:
            return files

    def _send_file(self, fpath: str) -> None:
        try:
            with open(fpath, "rb") as file:
                self.handler.conn.sendfile(file, 0)
        except Exception as e:
            self.msg("error", f"[!!] ERROR: Cant send file to client: '{self.handler.client}', error: {e} [!!]", sender=self.name)
        
    
    def send_files(self) -> None:
        self.msg("no-imp", f"Start send file to: '{self.handler.client}'", sender=self.name)
        files = self.find_files()
        if not files:
            self.msg("no-imp", f"[!!] WARNING: No files to send. Put file in: '{self.dir_input}'", sender=self.name)
            self.handler.close()
            return
        for file in files:
            self._send_file(file)
            sleep(1)
        self.handler.close()
    
    def run(self) -> None:
        sleep(0.5)
        self.send_files()
