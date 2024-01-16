import socket

from threading import Thread


class SocketHandler(Thread):
    def __init__(self, name: str, msg_socket: socket, cc_calback):
        super().__init__(daemon=True)
        self.name = name
        self.socket = msg_socket
        self.CC = cc_calback
        self.raw_len = self.CC.raw_len
        self.format = self.CC.format
        self.show = True
        self.buffer = []
    
    def recvMsg(self) -> str:
        msg = b""
        while True:
            recv = self.socket.recv(self.raw_len)
            if recv:
                if len(recv) < self.raw_len:
                    msg += recv
                    break
                else:
                    msg += recv
            else:
                return None
        msg = msg.decode(self.format)
        return msg
    
    def wait4msg(self) -> None:
        while True:
            msg = self.recvMsg()
            if not msg:
                break
            else:
                if self.show:
                    print("\n" + msg)
                else:
                    self.buffer.append(str(msg) + "\n")
    
    def emptyBuffer(self) -> None:
        for msg in self.buffer:
            print(msg)
    
    def close(self) -> None:
        try:
            self.socket.shutdown(socket.SHUT_RDWR)
            self.socket.close()
        except:
            pass
    
    def __del__(self) -> None:
        self.close()
    
    def run(self) -> None:
        self.wait4msg()



    
